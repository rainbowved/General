from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .rng_engine import RngEngine


@dataclass(frozen=True)
class SelectorResolutionError(ValueError):
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


def _norm_tags(tags_json: Any) -> Tuple[str, ...]:
    if tags_json is None:
        return tuple()
    if isinstance(tags_json, str):
        try:
            tags_json = json.loads(tags_json)
        except Exception:
            return tuple()
    if isinstance(tags_json, list):
        out: List[str] = []
        for t in tags_json:
            if isinstance(t, str) and t:
                out.append(t)
        return tuple(out)
    return tuple()


def _match_filter(flt: Mapping[str, Any], item: Mapping[str, Any]) -> bool:
    """Evaluate selector filters for an item definition.

    Supported keys (as of specs/ingredient_selectors.json):
    - type_in, group_in
    - tags_all, tags_any
    - item_id_prefix_any
    - any_of (list of filter dicts)
    - all_of (list of filter dicts)
    """

    # combinators
    any_of = flt.get("any_of")
    if isinstance(any_of, list):
        return any(_match_filter(x, item) for x in any_of if isinstance(x, dict))
    all_of = flt.get("all_of")
    if isinstance(all_of, list):
        return all(_match_filter(x, item) for x in all_of if isinstance(x, dict))

    item_id = item.get("item_id")
    itype = item.get("type")
    igroup = item.get("group")
    tags = _norm_tags(item.get("tags"))
    if not tags:
        tags = _norm_tags(item.get("tags_json"))
    tagset = set(tags)

    type_in = flt.get("type_in")
    if isinstance(type_in, list) and type_in:
        if not isinstance(itype, str) or itype not in type_in:
            return False

    group_in = flt.get("group_in")
    if isinstance(group_in, list) and group_in:
        if not isinstance(igroup, str) or igroup not in group_in:
            return False

    tags_all = flt.get("tags_all")
    if isinstance(tags_all, list) and tags_all:
        for t in tags_all:
            if isinstance(t, str) and t not in tagset:
                return False

    tags_any = flt.get("tags_any")
    if isinstance(tags_any, list) and tags_any:
        ok = False
        for t in tags_any:
            if isinstance(t, str) and t in tagset:
                ok = True
                break
        if not ok:
            return False

    pref_any = flt.get("item_id_prefix_any")
    if isinstance(pref_any, list) and pref_any:
        if not isinstance(item_id, str):
            return False
        ok = any(isinstance(p, str) and item_id.startswith(p) for p in pref_any)
        if not ok:
            return False

    return True


class SelectorResolver:
    """Resolves GROUP_* ingredient selectors into concrete item_id.

    Determinism policy:
    - candidates are collected in a stable order (sorted by item_id)
    - if rng is provided and initialized, ties are broken with RNG_CRAFT (u32 roll)
    - otherwise, the lexicographically smallest candidate is chosen
    """

    def __init__(
        self,
        selectors_spec: Mapping[str, Any],
        item_defs: Mapping[str, Mapping[str, Any]],
    ):
        selectors = selectors_spec.get("selectors")
        if not isinstance(selectors, dict):
            raise ValueError("ingredient_selectors.json: expected selectors object")
        self._selectors: Dict[str, Dict[str, Any]] = {
            k: dict(v) for k, v in selectors.items() if isinstance(k, str) and isinstance(v, dict)
        }
        self._items = item_defs

    def has_selector(self, selector_id: str) -> bool:
        return selector_id in self._selectors

    def list_selectors(self) -> List[str]:
        return sorted(self._selectors.keys())

    def list_candidates(
        self,
        selector_id: str,
        *,
        inventory_counts: Mapping[str, int],
        required_qty: int = 1,
    ) -> List[str]:
        sel = self._selectors.get(selector_id)
        if sel is None:
            raise SelectorResolutionError(f"Unknown selector: {selector_id}")
        flt = sel.get("filters")
        if not isinstance(flt, dict):
            raise SelectorResolutionError(f"Selector {selector_id}: missing/invalid 'filters'")

        rq = int(required_qty)
        if rq < 1:
            rq = 1

        cands: List[str] = []
        for item_id, cnt in inventory_counts.items():
            if not isinstance(item_id, str) or not item_id:
                continue
            if int(cnt) < rq:
                continue
            idef = self._items.get(item_id)
            if not isinstance(idef, Mapping):
                continue
            if _match_filter(flt, idef):
                cands.append(item_id)
        cands.sort()
        return cands

    def resolve(
        self,
        selector_id: str,
        *,
        inventory_counts: Mapping[str, int],
        required_qty: int = 1,
        rng: Optional[RngEngine] = None,
        rng_stream_id: str = "RNG_CRAFT",
    ) -> Tuple[str, Optional[int]]:
        """Return (item_id, roll_u32|None)."""

        cands = self.list_candidates(
            selector_id, inventory_counts=inventory_counts, required_qty=required_qty
        )
        if not cands:
            raise SelectorResolutionError(
                f"{selector_id}: нет кандидатов (в инвентаре нет подходящих предметов)"
            )
        if len(cands) == 1:
            return cands[0], None

        if rng is not None and rng.is_initialized:
            roll = int(rng.next_u32(rng_stream_id))
            idx = roll % len(cands)
            return cands[idx], roll

        return cands[0], None
