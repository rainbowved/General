from __future__ import annotations

import zipfile
from pathlib import Path

from wt_client.core.pack_smoke import smoke_check_pack


def _make_temp_zip(tmp_path: Path, *, with_required: bool = True) -> Path:
    zpath = tmp_path / "pack.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        if with_required:
            for d in ("concept/", "db_bundle/", "specs/", "demo/"):
                # Create an explicit directory entry and a placeholder file for realism.
                zf.writestr(d, "")
                zf.writestr(d + "README.txt", "placeholder")
        else:
            zf.writestr("something_else/README.txt", "placeholder")
    return zpath


def test_smoke_open_pack(tmp_path: Path) -> None:
    zpath = _make_temp_zip(tmp_path, with_required=True)
    rep = smoke_check_pack(str(zpath))
    assert rep.pack_path.endswith("pack.zip")
    assert rep.entries_at_root  # non-empty
