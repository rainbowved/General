from __future__ import annotations

from typing import Any, Dict, Mapping


def _cl(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def eval_formula(name: str, stats: Mapping[str, Any]) -> Dict[str, Any]:
    spd = float(stats.get("SPD", 0))
    s = float(stats.get("STR", 0))
    if name == "EffectiveSPD":
        v = _cl(spd, 1, 999)
    elif name == "ActionsPerTick":
        v = _cl(spd / 10.0, 0.1, 9.9)
    elif name == "InitiativeScore":
        v = _cl(spd * 1.5 + s * 0.5, 0, 9999)
    elif name == "MaxHP":
        v = _cl(50 + s * 5, 1, 9999)
    elif name == "FATMax":
        v = _cl(100 + s * 2, 1, 9999)
    else:
        raise KeyError(name)
    return {"value": round(v, 4), "explain_tree": {"formula": name, "inputs": dict(stats)}, "inputs_used": ["SPD", "STR"], "caps_applied": []}
