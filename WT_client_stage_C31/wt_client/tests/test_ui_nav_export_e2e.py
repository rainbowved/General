import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.node_interactions import NodeInteractions
from wt_client.core.rng_engine import RngEngine
from wt_client.core.action_dispatcher import ActionDispatcher
from wt_client.core.world_resolver import WorldResolver
from wt_client.core.save_store import SaveStore
from wt_client.core.recent_actions import get_cursor, set_cursor, get_recent_delta_events
from wt_client.core.turnpack_builder import TurnpackBuilder, TurnpackMeta
from wt_client.core.schema_validate import validate_turnpack


RC_ENV = "WT_TEST_PACK"
_p = os.environ.get(RC_ENV)
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
        names = set(z.namelist())
        for rel in wanted:
            src = prefix + rel
            if src not in names:
                if rel.endswith("session.json"):
                    continue
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


@pytest.mark.rc_pack
def test_ui_like_nav_action_export_turnpack_validates(tmp_path: Path):
    """E2E-ish: choose neighbor + choose an action -> export TURNPACK -> schema validate."""

    assert PACK_PATH is not None

    # Load pack
    pack = ContentPackLoader().load(str(PACK_PATH))
    schema = pack.load_json("specs/turnpack_schema.json")
    assert isinstance(schema, dict)
    schema_version = str(schema.get("$id") or "0.6.6-turnpack1")

    # Load demo save
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)
    cur = get_cursor(state) or {"seen_event_ids": []}

    # Build core objects (no UI)
    interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
    rng = RngEngine(pack.load_json("specs/rng_streams.json"))
    disp = ActionDispatcher(pack, interactions, rng)
    wr = WorldResolver(pack)

    # 1) Pick a neighbor and "move" (existing action type)
    neighbors = wr.get_neighbors(state)
    assert neighbors, "Demo world has no neighbors to navigate to"
    to_node_id = str(neighbors[0])
    res1 = disp.dispatch({"type": "move", "to_node_id": to_node_id}, state, cursor=cur)
    state = res1.new_state
    set_cursor(state, res1.new_cursor)
    assert any(ev.get("type") == "WORLD_MOVE" for ev in res1.applied_events)

    # 2) Pick *some* available node action (may be record-only) and dispatch it
    loc = ((((state.get("world") or {}).get("world") or {}).get("location") or {}))
    graph_id = str(loc.get("location_id") or "")
    node_id = str(loc.get("sub_id") or "")
    node = wr.get_node_by_id(state, node_id)
    ra = interactions.resolve(node)
    assert ra.action_ids, "No actions resolved for current node"
    action_id = str(ra.action_ids[0])
    cur2 = get_cursor(state) or res1.new_cursor
    res2 = disp.dispatch({"type": "node_action", "action_id": action_id}, state, cursor=cur2)
    state = res2.new_state
    set_cursor(state, res2.new_cursor)

    # 3) Export TURNPACK (same way UI does) and validate against schema
    delta_events = get_recent_delta_events(state, last_actions=10)
    meta = TurnpackMeta.from_state(state, schema_version=schema_version)
    tp = TurnpackBuilder().build(state, recent_actions=delta_events, meta=meta)
    ok, errors = validate_turnpack(tp, schema)
    assert ok, f"TURNPACK schema validation failed: {errors}"

    # Small sanity: exported location should be non-empty
    assert tp.get("snapshot_min", {}).get("location", {}).get("node_id")
