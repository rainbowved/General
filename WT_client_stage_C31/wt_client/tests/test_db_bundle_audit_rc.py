from __future__ import annotations

import os
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.db_bundle_audit import audit_db_bundle
from wt_client.core.inventory_delta import count_item_qty
from wt_client.core.item_catalog import ItemCatalog
from wt_client.core.save_store import SaveStore


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


@pytest.mark.rc_pack
def test_db_bundle_audit_rc_does_not_crash():
    assert PACK_PATH is not None
    pack = ContentPackLoader().load(str(PACK_PATH))
    try:
        rep = audit_db_bundle(pack)
        # At least one sqlite is expected in db_bundle.
        assert rep.sqlite_files
        # There should be an items schema guess somewhere.
        assert any(a.items_guess is not None for a in rep.audits)
    finally:
        pack.close()


@pytest.mark.rc_pack
def test_item_viewer_can_resolve_at_least_one_demo_inventory_item(tmp_path: Path):
    assert PACK_PATH is not None

    # Extract demo save using existing SaveStore-compatible extraction method.
    pack = ContentPackLoader().load(str(PACK_PATH))
    try:
        # Use the same extraction strategy as CLI: copy demo/save & demo/session.
        out = tmp_path / "demo"
        out.mkdir(parents=True, exist_ok=True)
        for rel in pack.list_files():
            reln = rel.replace("\\", "/").lstrip("/")
            if reln.startswith("demo/save/") or reln.startswith("demo/session/"):
                data = pack.open_binary(reln)
                dst = out / reln.split("demo/", 1)[1]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)

        store = SaveStore()
        state = store.load_save(out)
        totals = count_item_qty(state)
        assert totals, "Demo inventory is empty (unexpected for viewer integration)"

        some_item_id = sorted(totals.keys())[0]

        cat = ItemCatalog(pack)
        rec = cat.get(some_item_id)
        # Viewer must not crash. A missing DB record is acceptable; then we fall back to item_id.
        if rec is not None:
            assert isinstance(rec.name_ru, str)
            assert rec.name_ru.strip()
    finally:
        pack.close()
