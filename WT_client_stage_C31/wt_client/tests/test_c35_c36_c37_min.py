from __future__ import annotations

from wt_client.core.derived_stats import compute_derived
from wt_client.core.meter_engine import apply_meter_action
from wt_client.core.turn_engine import begin_turn, end_turn


def test_turn_engine_basic() -> None:
    st, ev1 = begin_turn({"session": {"active_turn": 0}})
    st, ev2 = end_turn(st)
    assert st["session"]["active_turn"] == 1
    assert ev1[0]["type"] == "SYS_TURN_BEGIN"
    assert ev2[0]["type"] == "SYS_TURN_END"


def test_derived_stats_min() -> None:
    d = compute_derived({"SPD": 20, "STR": 10})
    assert d["EffectiveSPD"]["value"] == 20
    assert d["MaxHP"]["value"] == 100


def test_meter_engine_actions() -> None:
    st = {"player": {"meters": {"fat_current": 50, "thirst": 50}}}
    st = apply_meter_action(st, "REST")
    assert st["player"]["meters"]["fat_current"] == 40
    st = apply_meter_action(st, "WATER_REFILL")
    assert st["player"]["meters"]["thirst"] == 35
