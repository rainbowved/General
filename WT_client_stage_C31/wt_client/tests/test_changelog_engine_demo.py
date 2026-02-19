import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.changelog_engine import ChangelogEngine
from wt_client.core.save_store import SaveStore


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


def _find_prefix(z: zipfile.ZipFile, tail: str) -> str:
    for n in z.namelist():
        if n.endswith(tail):
            return n[: -len(tail)]
    raise AssertionError(f"Could not locate {tail} inside the pack")


def _extract_demo_to(tmp_path: Path) -> Path:
    out = tmp_path / "demo_save"
    out.mkdir(parents=True, exist_ok=True)
    assert PACK_PATH is not None
    with zipfile.ZipFile(str(PACK_PATH), "r") as z:
        prefix = _find_prefix(z, "demo/save/player.json")
        wanted = [
            "demo/save/player.json",
            "demo/save/world.json",
            "demo/save/progress.json",
            "demo/save/inventory.json",
            "demo/session/session.json",
        ]
        for rel in wanted:
            src = prefix + rel
            if src not in z.namelist():
                if rel.endswith("session.json"):
                    continue
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


def _load_demo_changelog_events() -> list[dict]:
    assert PACK_PATH is not None
    with zipfile.ZipFile(str(PACK_PATH), "r") as z:
        prefix = _find_prefix(z, "demo/changelog/changelog.json")
        raw = z.read(prefix + "demo/changelog/changelog.json").decode("utf-8")
    import json

    doc = json.loads(raw)
    assert isinstance(doc, dict)
    events = doc.get("events")
    assert isinstance(events, list)
    return events


@pytest.mark.rc_pack
def test_demo_changelog_apply(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    store = SaveStore()
    state = store.load_save(demo_root)

    events = _load_demo_changelog_events()
    eng = ChangelogEngine()

    state2, cursor2, applied = eng.apply(events, state, cursor=None)
    assert applied == len(events)
    assert cursor2["seen_event_ids"]

    # World location moved.
    loc = state2["world"]["world"]["location"]
    assert loc["region"] == "OUTWALLS"
    assert loc["location_id"] == "OVERWALL"
    assert loc["sub_id"] == "POI_FO_R1_BOAR_WALLOW"

    # Inventory updated.
    items = state2["inventory"]["items"]
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["item_id"] == "ING_MEAT_RAW"
    assert items[0]["qty"] == 2


@pytest.mark.rc_pack
def test_demo_changelog_idempotent(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    store = SaveStore()
    state = store.load_save(demo_root)
    events = _load_demo_changelog_events()

    eng = ChangelogEngine()
    state2, cursor2, applied1 = eng.apply(events, state, cursor=None)
    state3, cursor3, applied2 = eng.apply(events, state2, cursor=cursor2)

    assert applied1 == len(events)
    assert applied2 == 0
    assert state2 == state3
    assert cursor2 == cursor3
