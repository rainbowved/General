from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.action_dispatcher import ActionDispatcher
from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.node_interactions import NodeInteractions
from wt_client.core.rng_engine import RngEngine
from wt_client.core.save_store import SaveStore
from wt_client.core.world_resolver import WorldResolver


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


def _find_prefix(z: zipfile.ZipFile, tail: str) -> str:
    for n in z.namelist():
        if n.endswith(tail):
            return n[: -len(tail)]
    raise AssertionError(f"Could not locate {tail} inside the pack")


def _extract_demo_to(tmp_path: Path, *, include_session: bool = True) -> Path:
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
        if include_session:
            wanted.append("demo/session/session.json")
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


def _add_stack(state: dict, item_id: str, qty: int, *, idx: int = 0) -> None:
    inv = state["inventory"]
    items = inv.setdefault("items", [])
    assert isinstance(items, list)
    items.append(
        {
            "instance_id": f"TEST_{item_id}_{idx}",
            "item_id": item_id,
            "qty": int(qty),
            "container": "bag",
            "slot": None,
            "equipped": False,
            "condition": 100,
        }
    )


@pytest.mark.rc_pack
def test_dispatch_move_commits_location(tmp_path: Path) -> None:
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
        rng = RngEngine(pack.load_json("specs/rng_streams.json"))
        rng.init("seed_move")
        dispatcher = ActionDispatcher(pack, interactions, rng)
        world = WorldResolver(pack)

        neigh = world.get_neighbors(state)
        assert neigh, "Expected at least one neighbor from demo location"
        to_id = neigh[0]

        res = dispatcher.dispatch({"type": "move", "to_node_id": to_id}, state, cursor=None)

    assert res.ok, f"dispatch failed: {res.errors}"
    assert any(ev.get("type") == "WORLD_MOVE" for ev in res.events)
    assert res.new_state["world"]["world"]["location"].get("sub_id") == to_id


@pytest.mark.rc_pack
def test_dispatch_idempotent_same_event_id(tmp_path: Path) -> None:
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
        rng = RngEngine(pack.load_json("specs/rng_streams.json"))
        rng.init("seed_move")
        dispatcher = ActionDispatcher(pack, interactions, rng)
        world = WorldResolver(pack)
        to_id = world.get_neighbors(state)[0]

        req = {"type": "move", "to_node_id": to_id}
        r1 = dispatcher.dispatch(req, state, cursor=None)
        assert r1.ok
        r2 = dispatcher.dispatch(req, r1.new_state, cursor=r1.new_cursor)

    assert r2.ok
    assert r2.events == []
    assert r2.new_state["world"]["world"]["location"].get("sub_id") == to_id


@pytest.mark.rc_pack
def test_dispatch_craft_changes_inventory(tmp_path: Path) -> None:
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)
    # Minimal controlled inventory
    state["inventory"]["items"] = []
    _add_stack(state, "R2", 1, idx=1)
    _add_stack(state, "R4", 1, idx=2)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
        rng = RngEngine(pack.load_json("specs/rng_streams.json"))
        rng.init("seed_craft")
        dispatcher = ActionDispatcher(pack, interactions, rng)

        res = dispatcher.dispatch({"type": "craft", "recipe_id": "RC_ALCH_POT_HEAL_MINOR", "times": 1}, state, cursor=None)

    assert res.ok, f"craft dispatch failed: {res.errors}"
    inv_ids = {it.get("item_id") for it in res.new_state["inventory"]["items"]}
    assert "POT_HEAL_MINOR" in inv_ids
    # Inputs consumed
    assert "R2" not in inv_ids
    assert "R4" not in inv_ids


@pytest.mark.rc_pack
def test_dispatch_unknown_action_noop(tmp_path: Path) -> None:
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path, include_session=False)
    state = SaveStore().load_save(demo_root)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
        rng = RngEngine(pack.load_json("specs/rng_streams.json"))
        rng.init("seed_noop")
        dispatcher = ActionDispatcher(pack, interactions, rng)

        # Demo cityhub node should expose SHOP_OPEN_BASIC but dispatcher doesn't implement it.
        res = dispatcher.dispatch({"type": "node_action", "action_id": "SHOP_OPEN_BASIC"}, state, cursor=None)

    assert res.ok
    # Known-but-not-implemented actions are safe no-op, but we still record action.request for TURNPACK.
    assert len(res.events) == 1
    assert res.events[0]["type"] == "action.request"
    # No gameplay mutation expected: location stays identical.
    assert res.new_state["world"]["world"]["location"] == state["world"]["world"]["location"]
