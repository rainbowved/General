from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .content_pack import ContentPack
from .rng_engine import RngEngine
from .inventory_delta import build_add_instances, apply_add_instances


def _stable_uuid(tag: str) -> str:
    b = hashlib.sha256(tag.encode("utf-8")).digest()[:16]
    bb = bytearray(b)
    bb[6] = (bb[6] & 0x0F) | 0x40
    bb[8] = (bb[8] & 0x3F) | 0x80
    h = bytes(bb).hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _xorshift32(x: int) -> int:
    x &= 0xFFFFFFFF
    x ^= (x << 13) & 0xFFFFFFFF
    x ^= (x >> 17) & 0xFFFFFFFF
    x ^= (x << 5) & 0xFFFFFFFF
    return x & 0xFFFFFFFF


@dataclass(frozen=True)
class LootResult:
    instance_id: str
    item_id: str
    qty: int


@dataclass(frozen=True)
class LootResolution:
    loot_pool_id: str
    loot_job_id: str
    instances: Tuple[LootResult, ...]
    events: Tuple[Dict[str, Any], ...]


class LootResolver:
    """Resolves a loot_pool_id into concrete item instances.

    MVP rule (no new mechanics):
    - each resolve performs N weighted picks from pool_items
    - quantity is sampled within [qty_min, qty_max]
    - instance_id and event_id are deterministic (hash-based)

    Source of truth: db_bundle/json/items_loot.json (as shipped).
    """

    def __init__(self, pack: ContentPack):
        self._pack = pack
        self._pool_items = self._load_pool_items()

    def _db_root(self) -> str:
        db = self._pack.layout.db_bundle_dir
        if not db:
            raise FileNotFoundError("db_bundle directory not found in pack")
        return db

    def _load_pool_items(self) -> Dict[str, List[Dict[str, Any]]]:
        path = f"{self._db_root()}/json/items_loot.json"
        doc = self._pack.load_json(path)
        pool_items = doc.get("pool_items")
        if not isinstance(pool_items, list):
            raise ValueError("items_loot.json: expected pool_items[]")
        out: Dict[str, List[Dict[str, Any]]] = {}
        for it in pool_items:
            if not isinstance(it, dict):
                continue
            pid = it.get("pool_id")
            if not isinstance(pid, str) or not pid:
                continue
            out.setdefault(pid, []).append(it)
        return out

    def pool_exists(self, pool_id: str) -> bool:
        return pool_id in self._pool_items

    def resolve_loot_pool(
        self,
        loot_pool_id: str,
        rng: RngEngine,
        *,
        stream_id: str = "RNG_LOOT",
        picks: int = 1,
        scope_id: Optional[str] = None,
        ts: Optional[str] = None,
    ) -> LootResolution:
        entries = self._pool_items.get(loot_pool_id)
        if not entries:
            raise ValueError(f"Unknown or empty loot_pool_id: {loot_pool_id}")

        scope = scope_id or loot_pool_id
        ts_val = ts or "1970-01-01T00:00:00Z"
        loot_job_id = _stable_uuid(f"loot_job|{scope}|{loot_pool_id}|{ts_val}")

        instances: List[LootResult] = []
        events: List[Dict[str, Any]] = []

        for i in range(int(picks)):
            before = rng.counter(stream_id)
            roll = rng.next_u32(stream_id)
            after = rng.counter(stream_id)

            entry = _weighted_choice(entries, roll)
            if entry is None:
                raise ValueError(f"Loot pool {loot_pool_id}: invalid weights")

            item_id = entry.get("item_id")
            if not isinstance(item_id, str) or not item_id:
                raise ValueError(f"Loot pool {loot_pool_id}: entry missing item_id")

            qmin = entry.get("qty_min")
            qmax = entry.get("qty_max")
            qmin_i = int(qmin) if isinstance(qmin, int) else 1
            qmax_i = int(qmax) if isinstance(qmax, int) else qmin_i
            if qmin_i < 1:
                qmin_i = 1
            if qmax_i < qmin_i:
                qmax_i = qmin_i
            span = qmax_i - qmin_i + 1
            # Derive qty from the same roll (no extra RNG consumption)
            h32 = int.from_bytes(hashlib.sha256(item_id.encode("utf-8")).digest()[:4], "little")
            qty_roll = _xorshift32(roll ^ 0x9E3779B9 ^ h32)
            qty = qmin_i + (qty_roll % span)

            instance_id = _stable_uuid(f"inst|{loot_pool_id}|{item_id}|{qty}|{roll}|{i}")
            instances.append(LootResult(instance_id=instance_id, item_id=item_id, qty=int(qty)))

            events.append(
                {
                    "event_id": _stable_uuid(
                        f"SYS_RNG_ADVANCE|{scope}|{loot_pool_id}|{before}|{after}|{i}"
                    ),
                    "ts": ts_val,
                    "source": "system",
                    "type": "SYS_RNG_ADVANCE",
                    "payload": {
                        "stream_id": stream_id,
                        "roll_index_before": int(before),
                        "roll_index_after": int(after),
                        "roll_kind": "u32",
                        "context": "loot.pick_item",
                        "scope_id": scope,
                        "result_digest": None,
                    },
                }
            )

        # Loot job event
        events.append(
            {
                "event_id": _stable_uuid(f"loot.generate|{loot_job_id}|{loot_pool_id}"),
                "ts": ts_val,
                "source": "system",
                "type": "loot.generate",
                "payload": {
                    "loot_job_id": loot_job_id,
                    "scope_id": scope,
                    "loot_pool_id": loot_pool_id,
                    "instances": [
                        {"instance_id": r.instance_id, "item_id": r.item_id, "qty": r.qty}
                        for r in instances
                    ],
                    "rng_context": "loot.pick_item",
                },
            }
        )

        return LootResolution(
            loot_pool_id=loot_pool_id,
            loot_job_id=loot_job_id,
            instances=tuple(instances),
            events=tuple(events),
        )

    def apply_loot_pool(
        self,
        loot_pool_id: str,
        state: Dict[str, Any],
        rng: RngEngine,
        *,
        stream_id: str = "RNG_LOOT",
        picks: int = 1,
        scope_id: Optional[str] = None,
        ts: Optional[str] = None,
        container_id: str = "BAG_MAIN",
    ) -> LootResolution:
        """Resolve loot and apply it to state.inventory as INVENTORY_ADD_INSTANCES events."""

        res = self.resolve_loot_pool(
            loot_pool_id,
            rng,
            stream_id=stream_id,
            picks=picks,
            scope_id=scope_id,
            ts=ts,
        )

        origin = {
            "kind": "loot",
            "loot_job_id": res.loot_job_id,
            "loot_pool_id": res.loot_pool_id,
            "scope_id": scope_id or loot_pool_id,
        }
        inst_min = [
            {"instance_id": r.instance_id, "item_id": r.item_id, "qty": int(r.qty)}
            for r in res.instances
        ]
        inst_full = build_add_instances(inst_min, container_id=container_id, origin=origin)
        apply_add_instances(state, inst_full)

        ts_val = ts or "1970-01-01T00:00:00Z"
        add_event = {
            "event_id": _stable_uuid(f"INVENTORY_ADD_INSTANCES|loot|{res.loot_job_id}"),
            "ts": ts_val,
            "source": "system",
            "type": "INVENTORY_ADD_INSTANCES",
            "payload": {
                "reason": "LOOT",
                "loot_job_id": res.loot_job_id,
                "loot_pool_id": res.loot_pool_id,
                "instances": inst_full,
            },
        }

        return LootResolution(
            loot_pool_id=res.loot_pool_id,
            loot_job_id=res.loot_job_id,
            instances=res.instances,
            events=tuple(list(res.events) + [add_event]),
        )


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
