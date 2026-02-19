from __future__ import annotations

import zipfile
from pathlib import Path

from wt_client.core.pack_smoke import smoke_check_pack


def test_smoke_supports_wrapped_pack(tmp_path: Path) -> None:
    zpath = tmp_path / "wrapped.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        # Single top-level wrapper folder
        zf.writestr("WRAP/demo/", "")
        zf.writestr("WRAP/specs/", "")
        zf.writestr("WRAP/db_bundle_v1/", "")
        zf.writestr("WRAP/concept_v0.odt", "x")
    rep = smoke_check_pack(str(zpath))
    assert rep.ok is True
    assert rep.root_prefix == "WRAP/"
