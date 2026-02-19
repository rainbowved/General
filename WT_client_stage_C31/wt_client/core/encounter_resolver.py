from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .content_pack import ContentPack
from .rng_engine import RngEngine
from .world_resolver import WorldResolver


@dataclass(frozen=True)
class EncounterSelection:
    node_id: str
    encounter_table_id: str
    entry_id: str
    spawn_band_id: str
    loot_pool_id: Optional[str]
    roll_u32: int


def _stable_uuid(tag: str) -> str:
    """Deterministic UUID-like string from sha256 (RFC4122-ish formatting).

    Not a real uuid namespace mechanism, but stable across runs.
    """

    b = hashlib.sha256(tag.encode("utf-8")).digest()[:16]
    # Set version=4 and variant=10
    bb = bytearray(b)
    bb[6] = (bb[6] & 0x0F) | 0x40
    bb[8] = (bb[8] & 0x3F) | 0x80
    h = bytes(bb).hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


class EncounterResolver:
    """Resolves encounters based on current node links + encounters tables.

    MVP rules (no new mechanics):
    - If the current node has links.encounter_table_id, an encounter is selected.
    - Selection is weighted over table.entries using RNG_SPAWN (by default).
    """

    def __init__(self, pack: ContentPack):
        self._pack = pack
        self._world = WorldResolver(pack)
        self._tables = self._load_tables()

    def _db_root(self) -> str:
        db = self._pack.layout.db_bundle_dir
        if not db:
            raise FileNotFoundError("db_bundle directory not found in pack")
        return db

    def _load_tables(self) -> Dict[str, Dict[str, Any]]:
        path = f"{self._db_root()}/content/encounters/encounter_tables.json"
        doc = self._pack.load_json(path)
        tables = doc.get("tables")
        if not isinstance(tables, list):
            raise ValueError("encounter_tables.json: expected tables[]")
        out: Dict[str, Dict[str, Any]] = {}
        for t in tables:
            if not isinstance(t, dict):
                continue
            tid = t.get("table_id")
            if isinstance(tid, str) and tid:
                out[tid] = t
        return out

    def get_current_node(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        return self._world.get_current_node(state)

    def maybe_spawn_encounter(
        self,
        state: Mapping[str, Any],
        rng: RngEngine,
        *,
        stream_id: str = "RNG_SPAWN",
    ) -> Tuple[Optional[EncounterSelection], List[Dict[str, Any]]]:
        """Return selected encounter or None + changelog events (minimal)."""

        node = self.get_current_node(state)
        node_id = str(node.get("node_id") or "")
        links = node.get("links")
        if not isinstance(links, dict):
            return None, []
        table_id = links.get("encounter_table_id")
        if not isinstance(table_id, str) or not table_id:
            return None, []

        table = self._tables.get(table_id)
        if not table:
            raise ValueError(f"Unknown encounter_table_id: {table_id}")
        entries = table.get("entries")
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"Encounter table {table_id} has no entries")

        before = rng.counter(stream_id)
        roll = rng.next_u32(stream_id)
        after = rng.counter(stream_id)

        entry = _weighted_choice(entries, roll)
        if entry is None:
            raise ValueError(f"Encounter table {table_id}: invalid weights")

        entry_id = entry.get("entry_id")
        spawn_band_id = entry.get("spawn_band_id")
        loot_pool_id = entry.get("loot_pool_id")
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(f"Encounter entry missing entry_id in {table_id}")
        if not isinstance(spawn_band_id, str) or not spawn_band_id:
            raise ValueError(f"Encounter entry missing spawn_band_id in {table_id}:{entry_id}")
        if loot_pool_id is not None and not isinstance(loot_pool_id, str):
            loot_pool_id = None

        sel = EncounterSelection(
            node_id=node_id,
            encounter_table_id=table_id,
            entry_id=entry_id,
            spawn_band_id=spawn_band_id,
            loot_pool_id=loot_pool_id,
            roll_u32=int(roll),
        )

        events = [
            {
                "event_id": _stable_uuid(f"SYS_RNG_ADVANCE|{node_id}|{table_id}|{before}|{after}"),
                "ts": _best_effort_ts(state),
                "source": "system",
                "type": "SYS_RNG_ADVANCE",
                "payload": {
                    "stream_id": stream_id,
                    "roll_index_before": int(before),
                    "roll_index_after": int(after),
                    "roll_kind": "u32",
                    "context": "encounter.pick_entry",
                    "scope_id": node_id,
                    "result_digest": None,
                },
            },
            {
                "event_id": _stable_uuid(f"encounter.select|{node_id}|{entry_id}|{roll}"),
                "ts": _best_effort_ts(state),
                "source": "system",
                "type": "encounter.select",
                "payload": {
                    "node_id": node_id,
                    "encounter_table_id": table_id,
                    "entry_id": entry_id,
                    "spawn_band_id": spawn_band_id,
                },
            },
        ]
        return sel, events

    def resolve_encounter_to_loot(self, encounter: EncounterSelection) -> Optional[str]:
        return encounter.loot_pool_id


def _best_effort_ts(state: Mapping[str, Any]) -> str:
    try:
        w = state.get("world")
        if isinstance(w, dict):
            ww = w.get("world")
            if isinstance(ww, dict):
                tm = ww.get("time")
                if isinstance(tm, dict):
                    ts = tm.get("ts_utc")
                    if isinstance(ts, str) and ts:
                        return ts
    except Exception:
        pass
    return "1970-01-01T00:00:00Z"


def _weighted_choice(entries: Sequence[Mapping[str, Any]], roll_u32: int) -> Optional[Mapping[str, Any]]:
    total = 0
    weights: List[int] = []
    for e in entries:
        w = e.get("weight")
        wi = int(w) if isinstance(w, int) else 0
        if wi < 0:
            wi = 0
        weights.append(wi)
        total += wi
    if total <= 0:
        return None
    r = int(roll_u32) % total
    acc = 0
    for e, w in zip(entries, weights):
        acc += w
        if r < acc:
            return e
    return entries[-1] if entries else None
