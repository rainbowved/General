from __future__ import annotations

from typing import Any, Dict, Mapping


def _cl(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(v)))


def apply_meter_action(state: Mapping[str, Any], action_id: str) -> Dict[str, Any]:
    out = dict(state)
    player = dict(out.get("player") or {})
    meters = dict(player.get("meters") or {})
    if action_id in {"REST", "CAMP_REST"}:
        meters["fat_current"] = _cl(int(meters.get("fat_current") or 0) - 10)
    if action_id == "WATER_REFILL":
        meters["thirst"] = _cl(int(meters.get("thirst") or 0) - 15)
    if action_id in {"PROCEED", "move"}:
        meters["fat_current"] = _cl(int(meters.get("fat_current") or 0) + 3)
        meters["thirst"] = _cl(int(meters.get("thirst") or 0) + 2)
    player["meters"] = meters
    out["player"] = player
    return out
