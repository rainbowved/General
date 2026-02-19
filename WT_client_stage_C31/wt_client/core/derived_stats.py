from __future__ import annotations

from typing import Any, Dict, Mapping

from wt_client.core.formula_engine import eval_formula


FORMULAS = ["EffectiveSPD", "ActionsPerTick", "InitiativeScore", "MaxHP", "FATMax"]


def compute_derived(base_stats: Mapping[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for f in FORMULAS:
        out[f] = eval_formula(f, base_stats)
    return out
