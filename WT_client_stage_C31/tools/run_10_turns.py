from __future__ import annotations

import json
from wt_client.core.json_canonical import canonical_json_dumps
from wt_client.core.turn_engine import advance_time, apply_action, begin_turn, end_turn


def run() -> dict:
    st = {"session": {"active_turn": 0, "time_ticks": 0}, "cursor": {"seen_event_ids": []}, "rng": {"streams": {"RNG_LOOT": {"counter": 0}}}}
    events = []
    actions = ["PROCEED", "REST", "WATER_REFILL", "move", "craft"]
    for i in range(10):
        st, ev = begin_turn(st)
        events += ev
        st, ev = apply_action(st, {"type": "node_action", "action_id": actions[i % len(actions)]})
        events += ev
        st, ev = advance_time(st, 1)
        events += ev
        st, ev = end_turn(st)
        events += ev
    return {"state": st, "events": events}


if __name__ == "__main__":
    r1 = run()
    r2 = run()
    assert r1["state"]["session"]["active_turn"] == 10
    assert canonical_json_dumps(r1) == canonical_json_dumps(r2)
    print(json.dumps(r1, ensure_ascii=False, indent=2))
