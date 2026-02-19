import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.changelog_engine import ChangelogEngine
from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.encounter_resolver import EncounterResolver
from wt_client.core.loot_resolver import LootResolver
from wt_client.core.rng_engine import RngEngine
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
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


@pytest.mark.rc_pack
def test_demo_loot_deterministic():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        streams = pack.load_json("specs/rng_streams.json")
        loot = LootResolver(pack)

        rng1 = RngEngine(streams)
        rng1.init("SEED_DEMO_LOOT")
        r1 = loot.resolve_loot_pool("POOL_COOK_BEAST_MEAT", rng1, picks=3)

        rng2 = RngEngine(streams)
        rng2.init("SEED_DEMO_LOOT")
        r2 = loot.resolve_loot_pool("POOL_COOK_BEAST_MEAT", rng2, picks=3)

    assert [(x.item_id, x.qty) for x in r1.instances] == [(x.item_id, x.qty) for x in r2.instances]
    assert [e["type"] for e in r1.events] == [e["type"] for e in r2.events]


@pytest.mark.rc_pack
def test_loot_pool_exists_on_demo_node(tmp_path: Path):
    assert PACK_PATH is not None
    # Move demo save to the overwall POI via demo changelog, then try selecting an encounter.
    demo_root = _extract_demo_to(tmp_path)
    state = SaveStore().load_save(demo_root)

    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        changelog = pack.load_json("demo/changelog/changelog.json")
        events = changelog.get("events")
        assert isinstance(events, list) and events
        state2, _, _ = ChangelogEngine().apply(events, state, cursor={"seen_event_ids": []})

        streams = pack.load_json("specs/rng_streams.json")
        rng = RngEngine(streams)
        rng.init("SEED_DEMO_ENC")

        enc = EncounterResolver(pack)
        sel, _ = enc.maybe_spawn_encounter(state2, rng)
        assert sel is not None, "Expected an encounter on demo overwall POI"
        pool_id = enc.resolve_encounter_to_loot(sel)
        assert isinstance(pool_id, str) and pool_id

        loot = LootResolver(pack)
        assert loot.pool_exists(pool_id), f"Expected loot pool to exist: {pool_id}"
