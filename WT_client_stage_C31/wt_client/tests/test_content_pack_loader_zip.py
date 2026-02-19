import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.validate_pack import validate_pack


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


@pytest.mark.rc_pack
def test_loader_zip_health_ok():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        rep = validate_pack(pack)
        assert rep.ok, f"Health FAIL: errors={rep.errors} warnings={rep.warnings}"


@pytest.mark.rc_pack
def test_loader_zip_can_open_json_and_sqlite():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        rng = pack.load_json("specs/rng_streams.json")
        assert rng is not None

        dbdir = pack.layout.db_bundle_dir
        assert dbdir is not None
        sqlite_files = [
            f
            for f in pack.list_files()
            if f.startswith(dbdir + "/")
            and f.lower().endswith(".sqlite")
            and "write" not in f.lower()
        ]
        assert sqlite_files, "Expected at least one sqlite in db_bundle"
        conn = pack.open_sqlite(sqlite_files[0])
        try:
            row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1").fetchone()
            assert row is not None
        finally:
            conn.close()
