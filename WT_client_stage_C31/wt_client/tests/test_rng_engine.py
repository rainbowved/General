import os
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.rng_engine import RngEngine, RngNotInitializedError


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


@pytest.mark.rc_pack
def test_no_use_before_init():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        spec = pack.load_json("specs/rng_streams.json")
        eng = RngEngine(spec)
        with pytest.raises(RngNotInitializedError):
            eng.next_u32("RNG_WORLD")


@pytest.mark.rc_pack
def test_determinism_same_seed_and_snapshot_restore():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        spec = pack.load_json("specs/rng_streams.json")

    seed = "DEMO_SEED_123"
    a = RngEngine(spec)
    b = RngEngine(spec)
    a.init(seed)
    b.init(seed)

    seq_a = [a.next_u32("RNG_WORLD") for _ in range(10)]
    seq_b = [b.next_u32("RNG_WORLD") for _ in range(10)]
    assert seq_a == seq_b

    # snapshot/restore preserves continuation
    snap = a.snapshot()
    c = RngEngine(spec)
    c.restore(snap)
    assert c.next_u32("RNG_WORLD") == a.next_u32("RNG_WORLD")


@pytest.mark.rc_pack
def test_stream_counter_increments_and_isolated():
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        spec = pack.load_json("specs/rng_streams.json")

    eng = RngEngine(spec)
    eng.init("SEED_X")

    assert eng.counter("RNG_WORLD") == 0
    assert eng.counter("RNG_LOOT") == 0

    _ = eng.next_u32("RNG_WORLD")
    assert eng.counter("RNG_WORLD") == 1
    assert eng.counter("RNG_LOOT") == 0

    eng.advance("RNG_WORLD", 7)
    assert eng.counter("RNG_WORLD") == 8
    assert eng.counter("RNG_LOOT") == 0
