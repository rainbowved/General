import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.save_store import SaveStore, SaveValidationError


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


def _extract_demo_to(tmp_path: Path) -> Path:
    """Extract demo save from the datapack into a temp directory.

    Returns a directory that matches the demo layout:
      <root>/save/*.json
      <root>/session/session.json
    """
    out = tmp_path / "demo_save"
    out.mkdir(parents=True, exist_ok=True)

    assert PACK_PATH is not None
    with zipfile.ZipFile(str(PACK_PATH), "r") as z:
        names = z.namelist()
        # Find root prefix (release candidate is wrapped).
        prefix = None
        for n in names:
            if n.endswith("demo/save/player.json"):
                prefix = n[: -len("demo/save/player.json")]
                break
        assert prefix is not None, "Could not locate demo/save/player.json inside the pack"

        wanted = [
            "demo/save/player.json",
            "demo/save/world.json",
            "demo/save/progress.json",
            "demo/save/inventory.json",
            "demo/session/session.json",
        ]
        for rel in wanted:
            src = prefix + rel
            if src not in names:
                # session is optional
                if rel.endswith("session.json"):
                    continue
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


@pytest.mark.rc_pack
def test_load_demo_save(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    store = SaveStore()
    state = store.load_save(demo_root)

    assert state["meta"]["save_id"]
    assert isinstance(state["player"], dict)
    assert isinstance(state["inventory"], dict)
    assert isinstance(state["world"], dict)
    assert isinstance(state["progress"], dict)


@pytest.mark.rc_pack
def test_save_roundtrip(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    store = SaveStore()
    state1 = store.load_save(demo_root)

    out_root = tmp_path / "roundtrip"
    store.save_save(out_root, state1)

    state2 = store.load_save(out_root)
    assert state1["meta"]["save_id"] == state2["meta"]["save_id"]

    # Structural equality for core docs.
    assert state1["player"] == state2["player"]
    assert state1["inventory"] == state2["inventory"]
    assert state1["world"] == state2["world"]
    assert state1["progress"] == state2["progress"]


def test_missing_file_validation(tmp_path: Path):
    root = tmp_path / "broken"
    root.mkdir()
    # Create only some required files.
    (root / "player.json").write_text("{}", encoding="utf-8")
    (root / "world.json").write_text("{}", encoding="utf-8")

    store = SaveStore()
    with pytest.raises(SaveValidationError) as ex:
        store.load_save(root)
    msg = str(ex.value)
    assert "progress.json" in msg or "inventory.json" in msg
