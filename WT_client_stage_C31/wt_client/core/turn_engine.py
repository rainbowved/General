from __future__ import annotations

import copy
from typing import Any, Dict, List, Mapping, Tuple


def _next_turn(state: Mapping[str, Any]) -> int:
    ses = state.get("session") if isinstance(state, Mapping) else {}
    if isinstance(ses, Mapping):
        return int(ses.get("active_turn") or 0) + 1
    return 1


def begin_turn(state: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    ns = copy.deepcopy(dict(state))
    ses = ns.setdefault("session", {})
    turn = _next_turn(ns)
    ses["active_turn"] = turn
    ev = {"event_id": f"sys-turn-begin-{turn:06d}", "type": "SYS_TURN_BEGIN", "payload": {"turn": turn}}
    return ns, [ev]


def end_turn(state: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    ns = copy.deepcopy(dict(state))
    turn = int((ns.get("session") or {}).get("active_turn") or 0)
    ev = {"event_id": f"sys-turn-end-{turn:06d}", "type": "SYS_TURN_END", "payload": {"turn": turn}}
    return ns, [ev]


def advance_time(state: Mapping[str, Any], dt_ticks: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    ns = copy.deepcopy(dict(state))
    ses = ns.setdefault("session", {})
    cur = int(ses.get("time_ticks") or 0)
    ses["time_ticks"] = cur + int(dt_ticks)
    ev = {"event_id": f"sys-time-{ses['time_ticks']:08d}", "type": "SYS_TIME_ADVANCE", "payload": {"dt_ticks": int(dt_ticks)}}
    return ns, [ev]


def apply_action(state: Mapping[str, Any], action_request: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    ns = copy.deepcopy(dict(state))
    turn = int((ns.get("session") or {}).get("active_turn") or 0)
    aid = str(action_request.get("action_id") or action_request.get("type") or "ACT")
    ev = {"event_id": f"act-{turn:06d}-{aid}", "type": "ACTION_APPLIED", "payload": dict(action_request)}
    return ns, [ev]
