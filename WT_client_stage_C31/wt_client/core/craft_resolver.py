from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from .content_pack import ContentPack
from .inventory_delta import InventoryDeltaError, apply_add_instances, consume_item_qty, count_item_qty
from .rng_engine import RngEngine
from .selector_resolver import SelectorResolver, SelectorResolutionError


def _stable_uuid(tag: str) -> str:
    b = hashlib.sha256(tag.encode("utf-8")).digest()[:16]
    bb = bytearray(b)
    bb[6] = (bb[6] & 0x0F) | 0x40
    bb[8] = (bb[8] & 0x3F) | 0x80
    h = bytes(bb).hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


@dataclass(frozen=True)
class CraftRecipe:
    recipe_id: str
    craft_kind: str
    result_item_id: str
    output_qty: int
    station_id: Optional[str]
    tier: Optional[str]
    ingredients: Tuple[Tuple[str, int], ...]  # (item_id or GROUP_*, qty)


@dataclass(frozen=True)
class CraftResult:
    recipe_id: str
    resolved_ingredients: Tuple[Tuple[str, int], ...]
    produced: Tuple[Dict[str, Any], ...]
    removed: Tuple[Dict[str, Any], ...]
    events: Tuple[Dict[str, Any], ...]


class CraftError(ValueError):
    pass


class CraftResolver:
    """MVP CraftResolver for recipes stored in db_bundle (SQLite).

    No new mechanics:
    - only checks inventory, consumes inputs, produces outputs
    - GROUP_* ingredients are resolved through specs/ingredient_selectors.json
    """

    def __init__(self, pack: ContentPack):
        self._pack = pack
        self._db_root = self._require_db_root()
        self._items_db_path = self._find_items_db()
        self._item_defs = self._load_item_defs()

        # GROUP_* ingredients are resolved either through specs/ingredient_selectors.json
        # (preferred, if present) or via a small built-in fallback for the known GROUPs
        # used by the current db_bundle.
        self._selector: Optional[SelectorResolver] = None
        self._selectors_spec: Optional[Mapping[str, Any]] = None
        specs = self._pack.layout.specs_dir
        if specs:
            sel_path = f"{specs}/ingredient_selectors.json"
            if sel_path in set(self._pack.list_files()):
                self._selectors_spec = self._pack.load_json(sel_path)
                self._selector = SelectorResolver(self._selectors_spec, self._item_defs)

    def _require_db_root(self) -> str:
        db = self._pack.layout.db_bundle_dir
        if not db:
            raise FileNotFoundError("db_bundle directory not found in pack")
        return db

    def _find_items_db(self) -> str:
        # Prefer rpg_items.sqlite, fallback to rpg_items_write.sqlite
        candidates = [f"{self._db_root}/rpg_items.sqlite", f"{self._db_root}/rpg_items_write.sqlite"]
        files = set(self._pack.list_files())
        for c in candidates:
            cc = c.replace("\\", "/")
            while cc.startswith("./"):
                cc = cc[2:]
            if cc in files:
                return cc
        raise FileNotFoundError("rpg_items.sqlite not found in db_bundle")

    def _open_db(self) -> sqlite3.Connection:
        return self._pack.open_sqlite(self._items_db_path)

    def _load_item_defs(self) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        con = self._open_db()
        try:
            cur = con.cursor()
            try:
                cur.execute('SELECT item_id, type, "group", rarity, tags_json, stackable, stack_max FROM items')
                rows = cur.fetchall()
                has_rarity = True
            except sqlite3.OperationalError:
                # Older/minimal schemas (tests) may not have rarity.
                cur.execute('SELECT item_id, type, "group", tags_json, stackable, stack_max FROM items')
                rows = [(a, b, c, None, d, e, f) for (a, b, c, d, e, f) in cur.fetchall()]
                has_rarity = False

            for item_id, itype, igroup, rarity, tags_json, stackable, stack_max in rows:
                if not isinstance(item_id, str) or not item_id:
                    continue
                tags: Any = []
                if isinstance(tags_json, str) and tags_json:
                    try:
                        tags = json.loads(tags_json)
                    except Exception:
                        tags = []
                out[item_id] = {
                    "item_id": item_id,
                    "type": itype,
                    "group": igroup,
                    "rarity": rarity if has_rarity else None,
                    "tags": tags,
                    "stackable": int(stackable) if isinstance(stackable, int) else 0,
                    "stack_max": int(stack_max) if isinstance(stack_max, int) else None,
                }
        finally:
            con.close()
        return out

    def _fallback_group_candidates(self, group_id: str) -> List[str]:
        # Conservative built-in mapping for the two GROUP_* currently used in db_bundle recipes.
        # This is *not* a new mechanic: it is a fallback when the formal selectors spec is absent.
        gid = str(group_id)
        if gid == "GROUP_HERITAGE_SERUM_ANY":
            c = [
                iid
                for iid, d in self._item_defs.items()
                if isinstance(d, dict)
                and d.get("type") == "SERUM"
                and d.get("rarity") == "legendary"
            ]
            return sorted(set(c))

        if gid == "GROUP_BOSS_LEG_MATERIAL_ANY":
            c = [
                iid
                for iid, d in self._item_defs.items()
                if isinstance(d, dict)
                and d.get("rarity") == "legendary"
                and d.get("type") in ("LEG_MATERIAL", "LEG_CORE")
            ]
            return sorted(set(c))

        return []

    def _list_group_candidates(self, group_id: str, *, counts: Mapping[str, int], qty: int) -> List[str]:
        if self._selector is not None:
            return self._selector.list_candidates(group_id, inventory_counts=counts, required_qty=qty)
        return self._fallback_group_candidates(group_id)

    def list_group_candidates(
        self,
        group_id: str,
        *,
        inventory_counts: Mapping[str, int],
        required_qty: int,
    ) -> List[str]:
        """Public helper used by CLI/demo tools."""
        return self._list_group_candidates(group_id, counts=inventory_counts, qty=int(required_qty))

    def get_recipe(self, recipe_id: str) -> CraftRecipe:
        if not isinstance(recipe_id, str) or not recipe_id:
            raise CraftError("recipe_id must be non-empty string")
        con = self._open_db()
        try:
            cur = con.cursor()
            cur.execute(
                'SELECT recipe_id, craft_kind, result_item_id, output_qty, station_id, tier FROM recipes WHERE recipe_id=?',
                (recipe_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise CraftError(f"Unknown recipe_id: {recipe_id}")
            rid, kind, res, out_qty, stn, tier = row
            cur.execute(
                'SELECT item_id, qty FROM recipe_ingredients WHERE recipe_id=? ORDER BY item_id',
                (recipe_id,),
            )
            ings: List[Tuple[str, int]] = []
            for item_id, qty in cur.fetchall():
                if isinstance(item_id, str) and item_id and isinstance(qty, int) and qty > 0:
                    ings.append((item_id, int(qty)))
            if not ings:
                raise CraftError(f"Recipe {recipe_id}: no ingredients")
            oq = int(out_qty) if isinstance(out_qty, int) else 1
            if oq < 1:
                oq = 1
            return CraftRecipe(
                recipe_id=str(rid),
                craft_kind=str(kind) if isinstance(kind, str) else "",
                result_item_id=str(res) if isinstance(res, str) else "",
                output_qty=oq,
                station_id=str(stn) if isinstance(stn, str) else None,
                tier=str(tier) if isinstance(tier, str) else None,
                ingredients=tuple(ings),
            )
        finally:
            con.close()

    def resolve_group_ingredients(
        self,
        recipe: CraftRecipe,
        *,
        state: Mapping[str, Any],
        rng: Optional[RngEngine] = None,
        rng_stream_id: str = "RNG_CRAFT",
    ) -> Tuple[Tuple[str, int], ...]:
        counts = count_item_qty(state)

        # Reserve explicit (non-GROUP) requirements to avoid selector self-collisions.
        need: Dict[str, int] = {}
        for iid, q in recipe.ingredients:
            if not iid.startswith("GROUP_"):
                need[iid] = need.get(iid, 0) + int(q)

        resolved: List[Tuple[str, int]] = []
        for item_id, qty in recipe.ingredients:
            if not item_id.startswith("GROUP_"):
                resolved.append((item_id, qty))
                continue

            candidates = self._list_group_candidates(item_id, counts=counts, qty=qty)
            feasible = [c for c in candidates if counts.get(c, 0) >= need.get(c, 0) + int(qty)]
            if not feasible:
                raise CraftError(
                    f"{item_id}: нет подходящих кандидатов (с учётом остальных ингредиентов)"
                )

            feasible.sort()
            if rng is not None and rng.is_initialized and len(feasible) > 1:
                roll = int(rng.next_u32(rng_stream_id))
                pick = feasible[roll % len(feasible)]
            else:
                pick = feasible[0]

            need[pick] = need.get(pick, 0) + int(qty)
            resolved.append((pick, qty))

        return tuple(resolved)

    def apply_craft(
        self,
        recipe_id: str,
        state: MutableMapping[str, Any],
        rng: RngEngine,
        *,
        ts: str = "1970-01-01T00:00:00Z",
        source: str = "player",
    ) -> CraftResult:
        recipe = self.get_recipe(recipe_id)

        # Resolve selectors first (feasibility-aware; may advance RNG_CRAFT on ties)
        counts = count_item_qty(state)
        events: List[Dict[str, Any]] = []

        # Reserve explicit ingredients to avoid choosing them as GROUP candidates unless there's enough qty.
        need: Dict[str, int] = {}
        for iid, q in recipe.ingredients:
            if not iid.startswith("GROUP_"):
                need[iid] = need.get(iid, 0) + int(q)

        resolved_ings: List[Tuple[str, int]] = []
        for item_id, qty in recipe.ingredients:
            if not item_id.startswith("GROUP_"):
                resolved_ings.append((item_id, qty))
                continue

            candidates = self._list_group_candidates(item_id, counts=counts, qty=qty)
            feasible = [c for c in candidates if counts.get(c, 0) >= need.get(c, 0) + int(qty)]
            if not feasible:
                raise CraftError(
                    f"{item_id}: нет подходящих кандидатов (с учётом остальных ингредиентов)"
                )
            feasible.sort()
            before = rng.counter("RNG_CRAFT")
            roll = None
            if rng.is_initialized and len(feasible) > 1:
                roll = int(rng.next_u32("RNG_CRAFT"))
                pick = feasible[roll % len(feasible)]
            else:
                pick = feasible[0]
            after = rng.counter("RNG_CRAFT")
            need[pick] = need.get(pick, 0) + int(qty)
            resolved_ings.append((pick, qty))
            if roll is not None:
                events.append(
                    {
                        "event_id": _stable_uuid(
                            f"SYS_RNG_ADVANCE|craft.selector|{item_id}|{before}|{after}"
                        ),
                        "ts": ts,
                        "source": "system",
                        "type": "SYS_RNG_ADVANCE",
                        "payload": {
                            "stream_id": "RNG_CRAFT",
                            "roll_index_before": int(before),
                            "roll_index_after": int(after),
                            "roll_kind": "u32",
                            "context": "craft.selector_pick",
                            "scope_id": item_id,
                            "result_digest": None,
                        },
                    }
                )

        # Validate availability (aggregate required qty)
        missing: List[str] = []
        for iid, req in sorted(need.items()):
            have = counts.get(iid, 0)
            if have < req:
                missing.append(f"{iid}: need {req}, have {have}")
        if missing:
            raise CraftError("Недостаточно ингредиентов: " + "; ".join(missing))

        # Consume ingredients
        removed_records: List[Dict[str, Any]] = []
        for iid, q in resolved_ings:
            try:
                removed_records.extend(consume_item_qty(state, item_id=iid, qty=q))
            except InventoryDeltaError as e:
                raise CraftError(str(e)) from e

        if removed_records:
            events.append(
                {
                    "event_id": _stable_uuid(
                        "INVENTORY_REMOVE_INSTANCES|" + recipe.recipe_id + "|" + "|".join(
                            f"{r['instance_id']}:{r['qty']}" for r in removed_records
                        )
                    ),
                    "ts": ts,
                    "source": source,
                    "type": "INVENTORY_REMOVE_INSTANCES",
                    "payload": {
                        "reason": "CRAFT_CONSUME",
                        "recipe_id": recipe.recipe_id,
                        "instances": [
                            {"instance_id": r["instance_id"], "qty": int(r["qty"])}
                            for r in removed_records
                        ],
                    },
                }
            )

        # Produce outputs
        out_defs = self._item_defs.get(recipe.result_item_id)
        stackable = int(out_defs.get("stackable")) if isinstance(out_defs, dict) else 0
        produced: List[Dict[str, Any]] = []
        digest_src = "|".join(sorted(f"{r['instance_id']}:{r['qty']}" for r in removed_records))
        digest = hashlib.sha256(digest_src.encode("utf-8")).hexdigest()[:16]
        if stackable == 1:
            produced.append(
                {
                    "instance_id": _stable_uuid(
                        f"CRAFT_OUT|{recipe.recipe_id}|{recipe.result_item_id}|{digest}|0"
                    ),
                    "item_id": recipe.result_item_id,
                    "qty": int(recipe.output_qty),
                }
            )
        else:
            for i in range(int(recipe.output_qty)):
                produced.append(
                    {
                        "instance_id": _stable_uuid(
                            f"CRAFT_OUT|{recipe.recipe_id}|{recipe.result_item_id}|{digest}|{i}"
                        ),
                        "item_id": recipe.result_item_id,
                        "qty": 1,
                    }
                )

        apply_add_instances(state, produced)

        if produced:
            events.append(
                {
                    "event_id": _stable_uuid(
                        "INVENTORY_ADD_INSTANCES|" + recipe.recipe_id + "|" + "|".join(
                            f"{p['instance_id']}:{p['item_id']}:{p['qty']}" for p in produced
                        )
                    ),
                    "ts": ts,
                    "source": source,
                    "type": "INVENTORY_ADD_INSTANCES",
                    "payload": {
                        "reason": "CRAFT_PRODUCE",
                        "recipe_id": recipe.recipe_id,
                        "instances": produced,
                    },
                }
            )

        return CraftResult(
            recipe_id=recipe.recipe_id,
            resolved_ingredients=tuple(resolved_ings),
            produced=tuple(produced),
            removed=tuple(removed_records),
            events=tuple(events),
        )


class CookResolver(CraftResolver):
    """Recipe runner restricted to COOKING craft_kind."""

    def get_recipe(self, recipe_id: str) -> CraftRecipe:  # type: ignore[override]
        r = super().get_recipe(recipe_id)
        if r.craft_kind != "COOKING":
            raise CraftError(f"Recipe {recipe_id} is not COOKING (got {r.craft_kind})")
        return r


class AlchemyResolver(CraftResolver):
    """Recipe runner restricted to ALCHEMY / ALCHEMY_ENDGAME craft_kind."""

    def get_recipe(self, recipe_id: str) -> CraftRecipe:  # type: ignore[override]
        r = super().get_recipe(recipe_id)
        if r.craft_kind not in ("ALCHEMY", "ALCHEMY_ENDGAME"):
            raise CraftError(f"Recipe {recipe_id} is not ALCHEMY (got {r.craft_kind})")
        return r
