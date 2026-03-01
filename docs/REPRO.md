# REPRO (PHASE 6)

## Determinism harness
Run twice and compare hash/state:

```bash
bash client/run_determinism.sh
```

Expected:
- `_logs/determinism.log` contains `[PASS] determinism`
- `client/_out/determinism_report.json` has `runs_equal=true`
- `state_hash` equals `client/scripts/golden_trace_expected_hash.txt`

## Full PHASE 6 CI
```bash
CI_LEVEL=full PHASE_TARGET=6 bash tools/ci.sh
```

This enforces required steps including `golden_compare` and `determinism`.
