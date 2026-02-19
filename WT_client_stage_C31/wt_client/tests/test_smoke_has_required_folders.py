from __future__ import annotations

import zipfile
from pathlib import Path

from wt_client.core.pack_smoke import smoke_check_pack, CANON_REQUIRED


def _make_temp_zip(tmp_path: Path, *, with_required: bool) -> Path:
    zpath = tmp_path / ("good.zip" if with_required else "bad.zip")
    with zipfile.ZipFile(zpath, "w") as zf:
        if with_required:
            for d in CANON_REQUIRED:
                zf.writestr(d, "")
        else:
            zf.writestr("concept/README.txt", "only concept present")
    return zpath


def test_smoke_has_required_folders(tmp_path: Path) -> None:
    good = _make_temp_zip(tmp_path, with_required=True)
    rep = smoke_check_pack(str(good))
    assert rep.ok is True
    assert set(rep.missing) == set()

    bad = _make_temp_zip(tmp_path, with_required=False)
    rep2 = smoke_check_pack(str(bad))
    assert rep2.ok is False
    assert len(rep2.missing) >= 1
