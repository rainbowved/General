from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Tuple


U64_MASK = (1 << 64) - 1
PCG32_MULT = 6364136223846793005


def _u64(x: int) -> int:
    return x & U64_MASK


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _derive_u64_pair(master_seed: Any, stream_id: str) -> Tuple[int, int]:
    """Derive (initstate, initseq) from master_seed and stream_id.

    Uses SHA-256 for stable cross-platform derivation.
    """
    ms = str(master_seed).encode("utf-8")
    sid = stream_id.encode("utf-8")
    h = _sha256(ms + b"|" + sid)
    a = int.from_bytes(h[0:8], "little")
    b = int.from_bytes(h[8:16], "little")
    return _u64(a), _u64(b)


def pcg32_seed(initstate: int, initseq: int) -> Tuple[int, int]:
    """Return (state, inc) for PCG32."""
    state = 0
    inc = _u64((initseq << 1) | 1)  # must be odd
    state = _u64(state * PCG32_MULT + inc)
    state = _u64(state + initstate)
    state = _u64(state * PCG32_MULT + inc)
    return state, inc


def pcg32_next_u32(state: int, inc: int) -> Tuple[int, int]:
    """Step and return (u32, new_state)."""
    oldstate = state
    state = _u64(oldstate * PCG32_MULT + inc)
    xorshifted = (((oldstate >> 18) ^ oldstate) >> 27) & 0xFFFFFFFF
    rot = (oldstate >> 59) & 31
    out = ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF
    return out, state


def pcg32_advance(state: int, inc: int, delta: int) -> int:
    """Skip-ahead for the LCG underlying PCG."""
    if delta <= 0:
        return state

    cur_mult = PCG32_MULT
    cur_plus = inc
    acc_mult = 1
    acc_plus = 0

    d = int(delta)
    while d > 0:
        if d & 1:
            acc_mult = _u64(acc_mult * cur_mult)
            acc_plus = _u64(acc_plus * cur_mult + cur_plus)
        cur_plus = _u64((cur_mult + 1) * cur_plus)
        cur_mult = _u64(cur_mult * cur_mult)
        d >>= 1
    return _u64(acc_mult * state + acc_plus)


def _stream_ids_from_spec(streams_spec: Mapping[str, Any]) -> List[str]:
    streams = streams_spec.get("streams")
    if not isinstance(streams, list):
        raise ValueError("rng_streams.json: expected 'streams' to be a list")
    out: List[str] = []
    for i, s in enumerate(streams):
        if not isinstance(s, dict):
            raise ValueError(f"rng_streams.json: streams[{i}] must be an object")
        sid = s.get("stream_id")
        if not isinstance(sid, str) or not sid:
            raise ValueError(f"rng_streams.json: streams[{i}].stream_id must be a non-empty string")
        out.append(sid)
    return out


LEGACY_MAP = {
    "world": "RNG_WORLD",
    "combat": "RNG_COMBAT",
    "injury": "RNG_INJURY",
    "loot": "RNG_LOOT",
    "craft": "RNG_CRAFT",
    "spawn": "RNG_SPAWN",
    "vendor": "RNG_VENDOR",
    "economy": "RNG_ECONOMY",
}


@dataclass
class RngStreamState:
    stream_id: str
    state: int  # u64
    inc: int  # u64 (odd)
    counter: int = 0

    def step_u32(self) -> int:
        out, new_state = pcg32_next_u32(self.state, self.inc)
        self.state = new_state
        self.counter += 1
        return out

    def advance(self, n: int) -> None:
        n = int(n)
        if n <= 0:
            return
        self.state = pcg32_advance(self.state, self.inc, n)
        self.counter += n


@dataclass
class RngState:
    """Serializable RNG state for multiple named streams."""

    schema: str
    master_seed: str
    streams: Dict[str, RngStreamState]

    @classmethod
    def init_from_seed(cls, master_seed: Any, streams_spec: Mapping[str, Any]) -> "RngState":
        stream_ids = _stream_ids_from_spec(streams_spec)
        ms = str(master_seed)
        streams: Dict[str, RngStreamState] = {}
        for sid in stream_ids:
            initstate, initseq = _derive_u64_pair(ms, sid)
            st, inc = pcg32_seed(initstate, initseq)
            streams[sid] = RngStreamState(stream_id=sid, state=st, inc=inc, counter=0)
        return cls(schema="rng_state.pcg32.v1", master_seed=ms, streams=streams)

    def serialize(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "engine": "pcg32",
            "master_seed": self.master_seed,
            "streams": {
                sid: {"state": str(_u64(s.state)), "inc": str(_u64(s.inc)), "counter": int(s.counter)}
                for sid, s in self.streams.items()
            },
        }

    @classmethod
    def deserialize(cls, data: Mapping[str, Any], streams_spec: Mapping[str, Any]) -> "RngState":
        """Load from serialized v1 or from legacy demo save rng_state."""
        if not isinstance(data, dict):
            raise ValueError("rng state: expected object")

        # v1
        if data.get("schema") == "rng_state.pcg32.v1":
            ms = data.get("master_seed")
            if not isinstance(ms, str):
                raise ValueError("rng state: master_seed must be string")
            streams_in = data.get("streams")
            if not isinstance(streams_in, dict):
                raise ValueError("rng state: streams must be object")

            wanted = set(_stream_ids_from_spec(streams_spec))
            streams: Dict[str, RngStreamState] = {}
            problems: List[str] = []

            for sid in sorted(wanted):
                obj = streams_in.get(sid)
                if not isinstance(obj, dict):
                    problems.append(f"missing stream '{sid}'")
                    continue
                try:
                    st = int(str(obj.get("state")))
                    inc = int(str(obj.get("inc")))
                    cnt = int(obj.get("counter"))
                except Exception:
                    problems.append(f"stream '{sid}': invalid state/inc/counter")
                    continue
                streams[sid] = RngStreamState(stream_id=sid, state=_u64(st), inc=_u64(inc) | 1, counter=cnt)

            if problems:
                raise ValueError("rng state: " + "; ".join(problems))
            return cls(schema="rng_state.pcg32.v1", master_seed=ms, streams=streams)

        # legacy (demo save)
        if "seed" in data and "streams" in data:
            seed = data.get("seed")
            streams_legacy = data.get("streams")
            if not isinstance(seed, str):
                raise ValueError("legacy rng_state: seed must be string")
            if not isinstance(streams_legacy, dict):
                raise ValueError("legacy rng_state: streams must be object")

            st = cls.init_from_seed(seed, streams_spec)
            for legacy_name, info in streams_legacy.items():
                if not isinstance(legacy_name, str) or not isinstance(info, dict):
                    continue
                idx = info.get("index")
                if not isinstance(idx, int) or idx < 0:
                    continue
                sid = LEGACY_MAP.get(legacy_name)
                if sid and sid in st.streams:
                    st.streams[sid].advance(idx)
            return st

        # compact (demo/session SYS_RNG_INIT payload)
        # {
        #   engine: 'pcg32', mode: 'compact',
        #   seeds: {run_seed: 'sha256(demo)', ...},
        #   streams: [{stream_id:'RNG_LOOT', counter: 2}, ...]
        # }
        if data.get("engine") == "pcg32" and data.get("mode") == "compact" and isinstance(data.get("seeds"), dict):
            seeds = data.get("seeds")
            assert isinstance(seeds, dict)
            seed = None
            if isinstance(seeds.get("run_seed"), str) and seeds.get("run_seed"):
                seed = seeds.get("run_seed")
            elif isinstance(seeds.get("world_seed"), str) and seeds.get("world_seed"):
                seed = seeds.get("world_seed")
            else:
                seed = "seed"

            st = cls.init_from_seed(seed, streams_spec)

            # Two supported compact encodings:
            # 1) streams: [{stream_id, counter}, ...]
            # 2) streams_state: {STREAM_ID: {counter}, ...}
            streams_list = data.get("streams")
            if isinstance(streams_list, list):
                for row in streams_list:
                    if not isinstance(row, dict):
                        continue
                    sid = row.get("stream_id")
                    ctr = row.get("counter")
                    if isinstance(sid, str) and isinstance(ctr, int) and sid in st.streams and ctr > 0:
                        st.streams[sid].advance(int(ctr))
            else:
                streams_state = data.get("streams_state")
                if not isinstance(streams_state, dict):
                    raise ValueError("compact rng_state: expected streams or streams_state")
                for sid, row in streams_state.items():
                    if not isinstance(sid, str) or sid not in st.streams:
                        continue
                    if not isinstance(row, dict):
                        continue
                    ctr = row.get("counter")
                    if isinstance(ctr, int) and ctr > 0:
                        st.streams[sid].advance(int(ctr))
            return st

        raise ValueError("rng state: unsupported format")
