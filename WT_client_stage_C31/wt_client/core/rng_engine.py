from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from .rng_state import RngState


log = logging.getLogger("wt_client.rng")


@dataclass
class RngNotInitializedError(RuntimeError):
    def __str__(self) -> str:  # pragma: no cover
        return "RngEngine: init() must be called before using next()/advance()"


class RngEngine:
    """Deterministic multi-stream RNG engine.

    - Streams are defined by specs/rng_streams.json
    - All streams exist after init, with counter=0.
    - Using RNG before init raises a clear error.
    - Snapshot/restore is JSON-friendly (RngState.serialize/deserialize).
    """

    def __init__(self, streams_spec: Mapping[str, Any]):
        self._spec = streams_spec
        self._state: Optional[RngState] = None

    @property
    def is_initialized(self) -> bool:
        return self._state is not None

    def init(self, master_seed: Any) -> None:
        self._state = RngState.init_from_seed(master_seed, self._spec)
        log.info("RNG initialized with %d streams", len(self._state.streams))

    def restore(self, serialized_rng_state: Mapping[str, Any]) -> None:
        self._state = RngState.deserialize(serialized_rng_state, self._spec)
        log.info("RNG restored with %d streams", len(self._state.streams))

    def snapshot(self) -> Dict[str, Any]:
        self._require_init()
        assert self._state is not None
        return self._state.serialize()

    def next_u32(self, stream_id: str) -> int:
        self._require_init()
        assert self._state is not None
        s = self._state.streams.get(stream_id)
        if s is None:
            raise KeyError(f"Unknown RNG stream_id: {stream_id}")
        return s.step_u32()

    def next_float01(self, stream_id: str) -> float:
        # [0, 1) from 32-bit integer
        return self.next_u32(stream_id) / 2**32

    def advance(self, stream_id: str, n: int) -> None:
        self._require_init()
        assert self._state is not None
        s = self._state.streams.get(stream_id)
        if s is None:
            raise KeyError(f"Unknown RNG stream_id: {stream_id}")
        s.advance(int(n))

    def counter(self, stream_id: str) -> int:
        self._require_init()
        assert self._state is not None
        s = self._state.streams.get(stream_id)
        if s is None:
            raise KeyError(f"Unknown RNG stream_id: {stream_id}")
        return int(s.counter)

    # --- helpers ---
    def _require_init(self) -> None:
        if self._state is None:
            raise RngNotInitializedError()
