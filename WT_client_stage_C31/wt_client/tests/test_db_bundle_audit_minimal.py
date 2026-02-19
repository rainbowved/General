from __future__ import annotations

import sqlite3
from pathlib import Path

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.db_bundle_audit import audit_db_bundle
from wt_client.core.item_catalog import ItemCatalog


def test_db_bundle_audit_and_item_catalog_minimal(tmp_path: Path):
    # Minimal sqlite: different table name, only item_id + name.
    db = tmp_path / "rpg_items.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE item_defs (item_id TEXT PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO item_defs(item_id, name) VALUES (?, ?)", ("IT_TEST", "Test Item"))
    conn.commit()
    conn.close()

    pack = ContentPackLoader().load(tmp_path)
    try:
        rep = audit_db_bundle(pack)
        assert any(p.endswith("rpg_items.sqlite") for p in rep.sqlite_files)
        # We should be able to guess items schema (table item_defs).
        any_guess = False
        for a in rep.audits:
            if a.items_guess is not None:
                any_guess = True
                assert a.items_guess.id_col.lower() == "item_id"
                assert (a.items_guess.name_col or "").lower() in ("name", "name_ru", "title")
        assert any_guess

        cat = ItemCatalog(pack)
        rec = cat.get("IT_TEST")
        assert rec is not None
        assert rec.name_ru == "Test Item"
    finally:
        pack.close()
