from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from wt_client.core.content_pack import ContentPack


log = logging.getLogger("wt_client.db_bundle_audit")


@dataclass(frozen=True)
class TableInfo:
    name: str
    columns: Tuple[str, ...]
    primary_key: Tuple[str, ...]


@dataclass(frozen=True)
class ItemsSchemaGuess:
    table: str
    id_col: str
    name_col: Optional[str]
    desc_col: Optional[str]
    rarity_col: Optional[str]
    tier_col: Optional[str]
    tags_col: Optional[str]
    extra_col: Optional[str]
    type_col: Optional[str]
    group_col: Optional[str]
    class_col: Optional[str]
    notes: Tuple[str, ...]


@dataclass(frozen=True)
class SqliteAudit:
    relpath: str
    tables: Tuple[TableInfo, ...]
    items_guess: Optional[ItemsSchemaGuess]


@dataclass(frozen=True)
class DbBundleAudit:
    sqlite_files: Tuple[str, ...]
    audits: Tuple[SqliteAudit, ...]


def _list_sqlite_files(pack: ContentPack) -> List[str]:
    files = [f.replace("\\", "/").lstrip("/") for f in pack.list_files()]
    cands = [f for f in files if f.lower().endswith(".sqlite")]
    # Prefer db_bundle folder if present.
    dbd = pack.layout.db_bundle_dir
    if dbd:
        pref = dbd.rstrip("/") + "/"
        in_db = [f for f in cands if f.startswith(pref)]
        if in_db:
            cands = in_db
    # Deterministic ordering.
    return sorted(set(cands), key=lambda s: (len(s), s))


def _table_info(conn: sqlite3.Connection, table: str) -> TableInfo:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    colnames = [str(r[1]) for r in cols]
    pk = [str(r[1]) for r in cols if int(r[5] or 0) > 0]
    return TableInfo(name=table, columns=tuple(colnames), primary_key=tuple(pk))


def _list_tables(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [str(r[0]) for r in rows]


def _score_items_table(columns: Sequence[str]) -> int:
    cols = {c.lower() for c in columns}
    if "item_id" not in cols:
        return -1

    score = 10
    # Name columns
    if "name_ru" in cols:
        score += 8
    if "name" in cols:
        score += 6
    if "title" in cols:
        score += 4
    if "name_en" in cols:
        score += 2

    # Helpful extras
    if "description" in cols or "desc" in cols:
        score += 2
    if "tags_json" in cols or "tags" in cols:
        score += 1
    if "rarity" in cols:
        score += 1
    if "tier" in cols:
        score += 1

    return score


def guess_items_schema(conn: sqlite3.Connection) -> Optional[ItemsSchemaGuess]:
    tables = _list_tables(conn)
    best: Optional[Tuple[int, str, List[str]]] = None
    for t in tables:
        ti = conn.execute(f"PRAGMA table_info({t})").fetchall()
        cols = [str(r[1]) for r in ti]
        score = _score_items_table(cols)
        if score < 0:
            continue
        if best is None or score > best[0] or (score == best[0] and t < best[1]):
            best = (score, t, cols)

    if best is None:
        return None

    _, table, cols = best
    cols_l = {c.lower(): c for c in cols}

    def pick(*names: str) -> Optional[str]:
        for n in names:
            if n.lower() in cols_l:
                return cols_l[n.lower()]
        return None

    notes: List[str] = []

    id_col = cols_l.get("item_id", "item_id")
    name_col = pick("name_ru", "name", "title", "name_en")
    if not name_col:
        notes.append("No human-readable name column found; viewer should fall back to item_id")

    guess = ItemsSchemaGuess(
        table=table,
        id_col=id_col,
        name_col=name_col,
        desc_col=pick("description", "desc"),
        rarity_col=pick("rarity"),
        tier_col=pick("tier"),
        tags_col=pick("tags_json", "tags"),
        extra_col=pick("extra_json", "extra"),
        type_col=pick("type"),
        group_col=pick("group"),
        class_col=pick("class", "class_"),
        notes=tuple(notes),
    )
    return guess


def audit_sqlite(conn: sqlite3.Connection, relpath: str) -> SqliteAudit:
    tables = _list_tables(conn)
    infos = tuple(_table_info(conn, t) for t in tables)
    items_guess = guess_items_schema(conn)
    return SqliteAudit(relpath=relpath, tables=infos, items_guess=items_guess)


def audit_db_bundle(pack: ContentPack) -> DbBundleAudit:
    """Read-only inspection of db_bundle.

    This function MUST NOT modify the pack. It only enumerates sqlite schemas and
    produces a best-effort map for item_id -> human name resolution.
    """

    sqlite_files = _list_sqlite_files(pack)
    audits: List[SqliteAudit] = []

    for rel in sqlite_files:
        try:
            conn = pack.open_sqlite(rel)
        except Exception as e:
            log.warning("Failed to open sqlite=%s: %s", rel, e)
            continue
        try:
            audits.append(audit_sqlite(conn, rel))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    return DbBundleAudit(sqlite_files=tuple(sqlite_files), audits=tuple(audits))
