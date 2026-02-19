from __future__ import annotations

from pathlib import Path

from wt_client.core.json_canonical import canonical_json_dumps
from tools.run_10_turns import run


def test_golden_turn10_matches() -> None:
    got = canonical_json_dumps(run())
    exp = Path("wt_client/tests/golden/turn10.json").read_text(encoding="utf-8")
    assert canonical_json_dumps(__import__("json").loads(exp)) == got
