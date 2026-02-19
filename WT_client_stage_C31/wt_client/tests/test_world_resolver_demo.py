import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.save_store import SaveStore
from wt_client.core.world_resolver import WorldResolver
from wt_client.core.turnpack_builder import TurnpackBuilder, TurnpackMeta


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
        ]
        for rel in wanted:
            src = prefix + rel
            if src not in z.namelist():
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


@pytest.mark.rc_pack
def test_actions_exist_for_demo_node(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        resolver = WorldResolver(pack)
        node = resolver.get_current_node(state)
        actions = resolver.get_available_actions(node, state)

    assert actions, "Expected non-empty action list for demo node"
    # Market should have at least one shop action.
    assert any(a.get("action_id") == "SHOP_OPEN_BASIC" for a in actions)


@pytest.mark.rc_pack
def test_move_updates_location_and_turnpack_snapshot(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        resolver = WorldResolver(pack)
        node = resolver.get_current_node(state)
        cur_id = node.get("node_id")
        assert cur_id

        # Pick a reachable neighbor deterministically.
        neigh = resolver.get_neighbors(state)
        assert neigh, "Expected at least one neighbor in demo cityhub graph"
        to_id = neigh[0]

        state2, move_event = resolver.move(to_id, state)

    loc2 = state2["world"]["world"]["location"]
    assert loc2.get("sub_id") == to_id

    # Ensure TURNPACK snapshot reflects the move.
    meta = TurnpackMeta(schema_version="test", content_version="test", db_bundle_version="test", cursor=0)
    tp = TurnpackBuilder().build(state2, recent_actions=[move_event], meta=meta)
    snap = tp["snapshot_min"]["location"]["node_id"]
    assert str(to_id) in snap
