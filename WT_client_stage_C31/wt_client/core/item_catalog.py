from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from wt_client.core.content_pack import ContentPack
from wt_client.core.db_bundle_audit import guess_items_schema, ItemsSchemaGuess


log = logging.getLogger("wt_client.item_catalog")


@dataclass(frozen=True)
class ItemRecord:
    item_id: str
    # Kept as name_ru for backwards compatibility with UI, but this is the
    # best-effort human-readable name (could be RU/EN depending on schema).
    name_ru: str
    type: str
    group: str
    class_: str
    tier: Optional[int]
    rarity: Optional[str]
    description: Optional[str]
    tags: tuple[str, ...]
    extra: Dict[str, Any]


class ItemCatalogError(RuntimeError):
    pass


class ItemCatalog:
    """Read-only item lookup from db_bundle (sqlite).

    Viewer utility only: never writes to DB and never interprets mechanics.
    Must degrade gracefully if the sqlite schema is missing optional columns.
    """

    def __init__(self, pack: ContentPack) -> None:
        self._pack = pack
        self._sqlite_rel = self._find_items_sqlite(pack)
        self._conn = pack.open_sqlite(self._sqlite_rel)
        self._schema: Optional[ItemsSchemaGuess] = guess_items_schema(self._conn)
        self._cache: Dict[str, ItemRecord] = {}
        if self._schema is None:
            raise ItemCatalogError(
                "db_bundle: could not locate an items table (expected a table with item_id column)"
            )

    @property
    def sqlite_relpath(self) -> str:
        return self._sqlite_rel

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    def get(self, item_id: str) -> Optional[ItemRecord]:
        if not isinstance(item_id, str) or not item_id:
            return None
        if item_id in self._cache:
            return self._cache[item_id]

        s = self._schema
        assert s is not None

        row = self._conn.execute(self._build_select_sql(s), (item_id,)).fetchone()
        if not row:
            return None

        # Row contract (see _build_select_sql):
        # 0 item_id
        # 1 name
        # 2 type
        # 3 group
        # 4 class
        # 5 tier
        # 6 rarity
        # 7 description
        # 8 tags_json
        # 9 extra_json

        tags: tuple[str, ...] = ()
        try:
            if row[8]:
                # Expected JSON list. If it's not JSON, best-effort fallback.
                try:
                    xs = json.loads(row[8])
                    if isinstance(xs, list):
                        tags = tuple(str(x) for x in xs)
                    elif isinstance(xs, str):
                        tags = (xs,)
                except Exception:
                    # maybe comma-separated
                    s2 = str(row[8])
                    tags = tuple(x.strip() for x in s2.split(",") if x.strip())
        except Exception:
            tags = ()

        extra: Dict[str, Any] = {}
        try:
            if row[9]:
                x = json.loads(row[9])
                if isinstance(x, dict):
                    extra = dict(x)
        except Exception:
            extra = {}

        name = str(row[1]) if row[1] is not None and str(row[1]).strip() else str(row[0])

        tier_val: Optional[int] = None
        try:
            if row[5] is not None:
                tier_val = int(row[5])
        except Exception:
            tier_val = None

        rec = ItemRecord(
            item_id=str(row[0]),
            name_ru=name,
            type=str(row[2]) if row[2] is not None else "",
            group=str(row[3]) if row[3] is not None else "",
            class_=str(row[4]) if row[4] is not None else "",
            tier=tier_val,
            rarity=str(row[6]) if row[6] is not None else None,
            description=str(row[7]) if row[7] is not None else None,
            tags=tags,
            extra=extra,
        )
        self._cache[item_id] = rec
        return rec

    @staticmethod
    def _safe_ident(ident: str) -> str:
        # Conservative sqlite identifier whitelist.
        if not ident or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_" for c in ident):
            raise ItemCatalogError(f"Unsafe sqlite identifier: {ident!r}")
        return f'"{ident}"'

    @classmethod
    def _build_select_sql(cls, s: ItemsSchemaGuess) -> str:
        t = cls._safe_ident(s.table)
        idc = cls._safe_ident(s.id_col)

        def col_or_null(name: Optional[str], alias: str) -> str:
            if name:
                return f"{cls._safe_ident(name)} AS {cls._safe_ident(alias)}"
            return f"NULL AS {cls._safe_ident(alias)}"

        name_expr = col_or_null(s.name_col, "name")
        type_expr = col_or_null(s.type_col, "type")
        group_expr = col_or_null(s.group_col, "group")
        class_expr = col_or_null(s.class_col, "class")
        tier_expr = col_or_null(s.tier_col, "tier")
        rarity_expr = col_or_null(s.rarity_col, "rarity")
        desc_expr = col_or_null(s.desc_col, "description")
        tags_expr = col_or_null(s.tags_col, "tags_json")
        extra_expr = col_or_null(s.extra_col, "extra_json")

        return (
            f"SELECT {idc} AS {cls._safe_ident('item_id')}, {name_expr}, {type_expr}, {group_expr}, {class_expr}, "
            f"{tier_expr}, {rarity_expr}, {desc_expr}, {tags_expr}, {extra_expr} "
            f"FROM {t} WHERE {idc}=?"
        )

    @staticmethod
    def _find_items_sqlite(pack: ContentPack) -> str:
        # Prefer read-only main DB.
        cands = [f for f in pack.list_files() if f.replace("\\", "/").endswith("rpg_items.sqlite")]
        if not cands:
            cands = [
                f
                for f in pack.list_files()
                if f.replace("\\", "/").endswith("rpg_items_write.sqlite")
            ]

        if not cands:
            raise ItemCatalogError("db_bundle: rpg_items.sqlite not found in the selected pack")

        # Deterministic choice: shortest path first, then lexicographic.
        cands = sorted(cands, key=lambda s: (len(s), s))
        chosen = cands[0]
        log.info("ItemCatalog using sqlite=%s", chosen)
        return chosen
