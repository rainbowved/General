import os
import tempfile
import zipfile
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.validate_pack import validate_pack


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


@pytest.mark.rc_pack
def test_loader_dir_health_ok_after_extract():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with tempfile.TemporaryDirectory(prefix="wt_pack_extract_") as td:
        td_path = Path(td)
        with zipfile.ZipFile(str(PACK_PATH), "r") as zf:
            zf.extractall(td_path)

        # Note: extracted structure is typically wrapped in a single root folder.
        with loader.load(str(td_path)) as pack:
            rep = validate_pack(pack)
            assert rep.ok, f"Health FAIL: errors={rep.errors} warnings={rep.warnings}"
