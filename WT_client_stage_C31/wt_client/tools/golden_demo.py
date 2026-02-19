from __future__ import annotations

import argparse
import json
from pathlib import Path

from wt_client.__main__ import _build_turnpack
from wt_client.core.action_dispatcher import ActionDispatcher
from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.node_interactions import NodeInteractions
from wt_client.core.rng_engine import RngEngine
from wt_client.core.save_store import SaveStore


def run_demo(pack_path: str) -> dict:
    with ContentPackLoader().load(pack_path) as pack:
        store = SaveStore()
        # minimal: load demo save from repo if present
        save = Path(".wt_cli_tmp/golden_demo")
        save.mkdir(parents=True, exist_ok=True)
        state = {"schema_version": "0.6.5-save1", "session": {"active_turn": 0}, "player": {"meters": {}}, "world": {"world": {"location": {}}}}
        try:
            state = store.load_save(Path("demo/save"))
        except Exception:
            pass
        spec = pack.load_json("specs/node_interactions.json")
        rng = RngEngine(pack.load_json("specs/rng_streams.json"))
        rng.init("golden-demo")
        disp = ActionDispatcher(pack, NodeInteractions(spec), rng)
        res = disp.dispatch({"type": "node_action", "action_id": "PROCEED"}, state, None)
        tp = _build_turnpack(res.new_state)
        return {"turnpack": tp, "events": res.events, "state": res.new_state}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["generate", "verify"])
    ap.add_argument("--pack", required=True)
    ap.add_argument("--golden", default="wt_client/tests/golden/demo_min.json")
    args = ap.parse_args()

    out = run_demo(args.pack)
    p = Path(args.golden)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if args.mode == "generate":
        p.write_text(payload + "\n", encoding="utf-8")
        print(f"generated {p}")
        return 0
    cur = p.read_text(encoding="utf-8").strip()
    if cur != payload:
        print("golden mismatch")
        return 1
    print("golden ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
