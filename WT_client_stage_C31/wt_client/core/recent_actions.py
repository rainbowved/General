from __future__ import annotations

import copy
from typing import Any, Dict, List, Mapping, Optional, Tuple


RECENT_ACTIONS_KEY = "recent_actions"
DEFAULT_MAX_ACTIONS = 25
DEFAULT_MAX_EVENTS = 300


def _ensure_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def get_turn_no(state: Mapping[str, Any]) -> Optional[int]:
    ses = state.get("session")
    if isinstance(ses, dict):
        t = ses.get("active_turn")
        return int(t) if isinstance(t, int) else None
    return None


def get_cursor(state: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    ses = state.get("session")
    if isinstance(ses, dict) and isinstance(ses.get("cursor"), dict):
        return dict(ses.get("cursor"))
    prog = state.get("progress")
    if isinstance(prog, dict) and isinstance(prog.get("cursor"), dict):
        return dict(prog.get("cursor"))
    return None


def set_cursor(state: Dict[str, Any], cursor: Dict[str, Any]) -> None:
    if isinstance(state.get("session"), dict):
        state["session"]["cursor"] = copy.deepcopy(cursor)
        return
    if isinstance(state.get("progress"), dict):
        state["progress"]["cursor"] = copy.deepcopy(cursor)
        return
    # Fallback: create progress section (safe, but keep minimal)
    state["progress"] = {"cursor": copy.deepcopy(cursor)}


def _recent_actions_list(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    prog = state.get("progress")
    if not isinstance(prog, dict):
        prog = {}
        state["progress"] = prog

    ra = prog.get(RECENT_ACTIONS_KEY)
    if not isinstance(ra, list):
        ra = []
        prog[RECENT_ACTIONS_KEY] = ra

    # Keep only dict entries.
    ra2: List[Dict[str, Any]] = [r for r in ra if isinstance(r, dict)]
    if ra2 is not ra:
        prog[RECENT_ACTIONS_KEY] = ra2
    return ra2


def append_recent_action(
    state: Dict[str, Any],
    action_request: Mapping[str, Any],
    events: List[Dict[str, Any]],
    *,
    max_actions: int = DEFAULT_MAX_ACTIONS,
) -> None:
    """Append one dispatch record to state['progress'].recent_actions.

    Stored as a small JSON-friendly object so UI/CLI can export deterministic TURNPACK.
    """
    ra = _recent_actions_list(state)

    turn_no = get_turn_no(state)

    # Keep only minimal event fields to reduce bloat.
    evs_min: List[Dict[str, Any]] = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        evs_min.append({
            "event_id": ev.get("event_id"),
            "ts": ev.get("ts"),
            "type": ev.get("type"),
            "payload": ev.get("payload"),
        })

    rec: Dict[str, Any] = {
        "turn_no": turn_no,
        "action": dict(action_request),
        "event_ids": [str(e.get("event_id")) for e in evs_min if isinstance(e.get("event_id"), str)],
        "events": evs_min,
    }
    ra.append(rec)

    try:
        max_actions = int(max_actions)
    except Exception:
        max_actions = DEFAULT_MAX_ACTIONS
    max_actions = max(1, min(max_actions, 200))

    if len(ra) > max_actions:
        del ra[: len(ra) - max_actions]


def get_recent_delta_events(
    state: Mapping[str, Any],
    *,
    last_actions: int = 10,
    max_events: int = DEFAULT_MAX_EVENTS,
) -> List[Dict[str, Any]]:
    """Flatten last N recent_actions into a deterministic list of delta_events."""
    prog = state.get("progress")
    if not isinstance(prog, dict):
        return []

    ra = prog.get(RECENT_ACTIONS_KEY)
    if not isinstance(ra, list) or not ra:
        return []

    # Keep only dict items.
    items: List[Dict[str, Any]] = [r for r in ra if isinstance(r, dict)]
    if not items:
        return []

    try:
        last_actions = int(last_actions)
    except Exception:
        last_actions = 10
    last_actions = max(1, min(last_actions, 100))

    tail = items[-last_actions:]

    out: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for rec in tail:
        evs = rec.get("events")
        if not isinstance(evs, list):
            continue
        for ev in evs:
            if not isinstance(ev, dict):
                continue
            eid = ev.get("event_id")
            if isinstance(eid, str) and eid in seen:
                continue
            if isinstance(eid, str):
                seen.add(eid)
            out.append(dict(ev))
            if len(out) >= max_events:
                return out

    return out
