from __future__ import annotations

import copy
import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Tuple


log = logging.getLogger("wt_client.changelog")


@dataclass
class ChangelogApplyError(Exception):
    problems: List[str]

    def __str__(self) -> str:  # pragma: no cover
        lines = ["Changelog apply failed:"]
        lines.extend([f"- {p}" for p in self.problems])
        return "\n".join(lines)


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _normalize_cursor(cursor: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Cursor is JSON-friendly: stores last N event_ids + a digest."""
    if not cursor:
        return {"schema": "cursor_v1", "max_size": 10000, "seen_event_ids": [], "seen_hash": _sha256_hex("")}

    if not isinstance(cursor, dict):
        return {"schema": "cursor_v1", "max_size": 10000, "seen_event_ids": [], "seen_hash": _sha256_hex("")}

    max_size = cursor.get("max_size", 10000)
    try:
        max_size = int(max_size)
    except Exception:
        max_size = 10000
    max_size = max(1, min(max_size, 200000))

    seen = cursor.get("seen_event_ids", [])
    if not isinstance(seen, list):
        seen = []
    # Keep only strings, keep order.
    seen = [x for x in seen if isinstance(x, str)]
    if len(seen) > max_size:
        seen = seen[-max_size:]
    digest = cursor.get("seen_hash")
    if not isinstance(digest, str):
        digest = _sha256_hex("\n".join(seen))
    return {"schema": "cursor_v1", "max_size": max_size, "seen_event_ids": seen, "seen_hash": digest}


def _cursor_seen_set(cursor: Dict[str, Any]) -> set[str]:
    seen = cursor.get("seen_event_ids", [])
    return set(seen) if isinstance(seen, list) else set()


def _cursor_add(cursor: Dict[str, Any], event_id: str) -> None:
    seen: List[str] = cursor.get("seen_event_ids")  # type: ignore[assignment]
    if not isinstance(seen, list):
        seen = []
        cursor["seen_event_ids"] = seen
    if event_id in seen:
        return
    seen.append(event_id)
    max_size = int(cursor.get("max_size", 10000))
    if len(seen) > max_size:
        del seen[: len(seen) - max_size]
    cursor["seen_hash"] = _sha256_hex("\n".join(seen))


def _ensure_dict(d: Any, *, path: str, problems: List[str]) -> Optional[MutableMapping[str, Any]]:
    if not isinstance(d, dict):
        problems.append(f"{path}: expected object, got {type(d).__name__}")
        return None
    return d


class ChangelogEngine:
    """Applies CHANGELOG events to a GameState.

    - Idempotency is achieved via cursor event_id de-duplication.
    - Event application is atomic at the document-section level.
    - Only demo-observed event types are handled.
    """

    @staticmethod
    def supported_event_types() -> set[str]:
        """Event types that are explicitly handled (including intentional no-op narrative types)."""
        return {
            "WORLD_MOVE",
            "SYS_TURN_BEGIN",
            "SYS_TURN_END",
            "SYS_RNG_INIT",
            "SYS_RNG_ADVANCE",
            "MODE_SET",
            "INVENTORY_ADD_INSTANCES",
            "INVENTORY_REMOVE_INSTANCES",
            "METER_SET",
            # Narrative / informational events observed in demo flows (no mutation by design).
            "encounter.select",
            "combat.start",
            "combat.end",
            "loot.generate",
            "action.request",
            "craft.request",
        }

    def apply(
        self,
        changelog_events: Iterable[Dict[str, Any]],
        state: Dict[str, Any],
        cursor: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], int]:
        cur = _normalize_cursor(cursor)
        seen = _cursor_seen_set(cur)

        new_state: Dict[str, Any] = copy.deepcopy(state)
        applied = 0
        problems: List[str] = []

        for idx, ev in enumerate(changelog_events):
            if not isinstance(ev, dict):
                problems.append(f"events[{idx}]: expected object, got {type(ev).__name__}")
                continue

            eid = ev.get("event_id")
            etype = ev.get("type")
            payload = ev.get("payload")

            if not isinstance(eid, str) or not eid:
                problems.append(f"events[{idx}]: missing/invalid event_id")
                continue
            if not isinstance(etype, str) or not etype:
                problems.append(f"events[{idx}]({eid}): missing/invalid type")
                continue

            if eid in seen:
                continue

            try:
                self._apply_one(etype, payload, ev, new_state)
            except Exception as e:
                problems.append(f"events[{idx}]({eid})[{etype}]: {e}")
                continue

            _cursor_add(cur, eid)
            seen.add(eid)
            applied += 1

        if problems:
            raise ChangelogApplyError(problems)

        return new_state, cur, applied

    # --- handlers ---
    def _apply_one(self, etype: str, payload: Any, ev: Dict[str, Any], state: Dict[str, Any]) -> None:
        """Apply a single event atomically."""
        snap: Dict[str, Any] = {}

        def _snap(section: str) -> MutableMapping[str, Any]:
            cur = state.get(section)
            if not isinstance(cur, dict):
                cur = {}
            snap[section] = copy.deepcopy(cur)
            state[section] = copy.deepcopy(cur)
            return state[section]

        try:
            if etype == "WORLD_MOVE":
                w = _snap("world")
                self._apply_world_move(w, payload)
                return

            if etype == "SYS_TURN_BEGIN":
                s = _snap("session")
                self._apply_turn_begin(s, payload)
                return

            if etype == "SYS_TURN_END":
                s = _snap("session")
                m = state.get("meta")
                if not isinstance(m, dict):
                    m = {}
                state["meta"] = copy.deepcopy(m)
                self._apply_turn_end(state["meta"], s, payload)
                return

            if etype == "SYS_RNG_INIT":
                s = _snap("session")
                self._apply_rng_init(s, payload)
                return

            if etype == "SYS_RNG_ADVANCE":
                s = _snap("session")
                self._apply_rng_advance(s, payload)
                return

            if etype == "MODE_SET":
                s = _snap("session")
                self._apply_mode_set(s, payload)
                return

            if etype == "INVENTORY_ADD_INSTANCES":
                inv = _snap("inventory")
                self._apply_inventory_add(inv, payload)
                return

            if etype == "INVENTORY_REMOVE_INSTANCES":
                inv = _snap("inventory")
                self._apply_inventory_remove(inv, payload)
                return

            # Demo narrative / info events: no mutation by design.
            if etype in {"encounter.select", "combat.start", "combat.end", "loot.generate", "action.request", "craft.request"}:
                return

            # Unknown type: safe no-op.
            log.warning("Ignoring unsupported changelog event type: %s", etype)

        except Exception:
            for k, v in snap.items():
                state[k] = v
            raise

    def _apply_world_move(self, world_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="WORLD_MOVE.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))

        to_d = _ensure_dict(p.get("to"), path="WORLD_MOVE.payload.to", problems=probs)
        if to_d is None:
            raise ValueError("; ".join(probs))

        w_d = _ensure_dict(world_doc.get("world"), path="world.world", problems=probs)
        if w_d is None:
            raise ValueError("; ".join(probs))

        loc_d = _ensure_dict(w_d.get("location"), path="world.world.location", problems=probs)
        if loc_d is None:
            loc_d = {}
            w_d["location"] = loc_d

        for key in ("region", "location_id", "sub_id"):
            val = to_d.get(key)
            if not isinstance(val, str) or not val:
                probs.append(f"WORLD_MOVE.payload.to.{key}: missing/invalid")
            else:
                loc_d[key] = val

        note = p.get("note")
        if isinstance(note, str) and note:
            loc_d["notes"] = note

        if probs:
            raise ValueError("; ".join(probs))

    def _apply_turn_begin(self, session_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="SYS_TURN_BEGIN.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))
        turn_no = p.get("turn_no")
        if not isinstance(turn_no, int):
            raise ValueError("SYS_TURN_BEGIN.payload.turn_no: expected int")
        session_doc["active_turn"] = turn_no

    def _apply_turn_end(self, meta: MutableMapping[str, Any], session_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="SYS_TURN_END.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))
        turn_no = p.get("turn_no")
        if isinstance(turn_no, int):
            session_doc["active_turn"] = turn_no
        chk = p.get("state_checksum")
        if isinstance(chk, str) and chk:
            meta["last_state_checksum"] = chk

    def _apply_rng_init(self, session_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="SYS_RNG_INIT.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))

        engine = p.get("engine")
        mode = p.get("mode")
        seeds = p.get("seeds")
        streams = p.get("streams")

        if not isinstance(engine, str):
            probs.append("SYS_RNG_INIT.payload.engine: expected str")
        if not isinstance(mode, str):
            probs.append("SYS_RNG_INIT.payload.mode: expected str")
        if not isinstance(seeds, dict):
            probs.append("SYS_RNG_INIT.payload.seeds: expected object")
        if not isinstance(streams, list):
            probs.append("SYS_RNG_INIT.payload.streams: expected list")
        if probs:
            raise ValueError("; ".join(probs))

        streams_state: Dict[str, Dict[str, int]] = {}
        for i, s in enumerate(streams):
            if not isinstance(s, dict):
                raise ValueError(f"SYS_RNG_INIT.payload.streams[{i}]: expected object")
            sid = s.get("stream_id")
            cnt = s.get("counter")
            if not isinstance(sid, str) or not sid:
                raise ValueError(f"SYS_RNG_INIT.payload.streams[{i}].stream_id: expected str")
            if not isinstance(cnt, int):
                raise ValueError(f"SYS_RNG_INIT.payload.streams[{i}].counter: expected int")
            streams_state[sid] = {"counter": cnt}

        session_doc["rng_state"] = {
            "engine": engine,
            "mode": mode,
            "seeds": seeds,
            "streams_state": streams_state,
        }

    def _apply_rng_advance(self, session_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="SYS_RNG_ADVANCE.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))
        sid = p.get("stream_id")
        after = p.get("roll_index_after")
        if not isinstance(sid, str) or not sid:
            raise ValueError("SYS_RNG_ADVANCE.payload.stream_id: expected str")
        if not isinstance(after, int):
            raise ValueError("SYS_RNG_ADVANCE.payload.roll_index_after: expected int")

        rng = session_doc.get("rng_state")
        if not isinstance(rng, dict):
            rng = {"engine": None, "mode": None, "seeds": {}, "streams_state": {}}
            session_doc["rng_state"] = rng
        st = rng.get("streams_state")
        if not isinstance(st, dict):
            st = {}
            rng["streams_state"] = st
        entry = st.get(sid)
        if not isinstance(entry, dict):
            st[sid] = {"counter": after}
        else:
            entry["counter"] = after

    def _apply_mode_set(self, session_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="MODE_SET.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))
        mode = p.get("mode")
        if not isinstance(mode, str) or not mode:
            raise ValueError("MODE_SET.payload.mode: expected non-empty string")
        session_doc["active_mode"] = mode

    def _apply_inventory_add(self, inv_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="INVENTORY_ADD_INSTANCES.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))

        inst = p.get("instances")
        if not isinstance(inst, list):
            raise ValueError("INVENTORY_ADD_INSTANCES.payload.instances: expected list")

        items = inv_doc.get("items")
        if items is None:
            items = []
            inv_doc["items"] = items
        if not isinstance(items, list):
            raise ValueError("inventory.items: expected list")

        for i, it in enumerate(inst):
            if not isinstance(it, dict):
                raise ValueError(f"instances[{i}]: expected object")
            iid = it.get("instance_id")
            item_id = it.get("item_id")
            qty = it.get("qty")
            if not isinstance(iid, str) or not iid:
                raise ValueError(f"instances[{i}].instance_id: expected str")
            if not isinstance(item_id, str) or not item_id:
                raise ValueError(f"instances[{i}].item_id: expected str")
            if not isinstance(qty, int) or qty < 1:
                raise ValueError(f"instances[{i}].qty: expected int >= 1")

            # Keep full instance dict (location/origin/etc) for forward compatibility.
            items.append(copy.deepcopy(it))


    def _apply_meter_set(self, meters_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="METER_SET.payload", problems=probs)
        key = p.get("key")
        value = p.get("value")
        if not isinstance(key, str) or not key:
            probs.append("METER_SET.payload.key: expected string")
        if not isinstance(value, (int, float)):
            probs.append("METER_SET.payload.value: expected number")
        if probs:
            raise ValueError("; ".join(probs))
        meters_doc[key] = int(value)
    def _apply_inventory_remove(self, inv_doc: MutableMapping[str, Any], payload: Any) -> None:
        probs: List[str] = []
        p = _ensure_dict(payload, path="INVENTORY_REMOVE_INSTANCES.payload", problems=probs)
        if p is None:
            raise ValueError("; ".join(probs))

        inst = p.get("instances")
        if not isinstance(inst, list):
            raise ValueError("INVENTORY_REMOVE_INSTANCES.payload.instances: expected list")

        items = inv_doc.get("items")
        if items is None:
            items = []
            inv_doc["items"] = items
        if not isinstance(items, list):
            raise ValueError("inventory.items: expected list")

        index: Dict[str, Dict[str, Any]] = {}
        for it in items:
            if isinstance(it, dict) and isinstance(it.get("instance_id"), str):
                index[it["instance_id"]] = it

        problems: List[str] = []
        for i, rec in enumerate(inst):
            if not isinstance(rec, dict):
                problems.append(f"instances[{i}]: expected object")
                continue
            iid = rec.get("instance_id")
            qty = rec.get("qty", 1)
            if not isinstance(iid, str) or not iid:
                problems.append(f"instances[{i}].instance_id: expected str")
                continue
            if not isinstance(qty, int) or qty < 1:
                problems.append(f"instances[{i}].qty: expected int >= 1")
                continue
            cur = index.get(iid)
            if cur is None:
                problems.append(f"missing instance_id: {iid}")
                continue
            have = cur.get("qty", 1)
            if not isinstance(have, int) or have < 0:
                problems.append(f"{iid}: invalid existing qty")
                continue
            if have < qty:
                problems.append(f"{iid}: not enough qty ({have} < {qty})")
                continue
            cur["qty"] = have - qty

        # Purge zero-qty entries.
        inv_doc["items"] = [it for it in items if not (isinstance(it, dict) and it.get("qty") == 0)]

        if problems:
            raise ValueError("; ".join(problems))
