# CI_LOG_LAYOUT.md

CI writes runtime logs and status markers to `_logs/` during local/CI execution.
These files are generated outputs and are intentionally **not tracked in git**.

## Log files (generated)
- `_logs/ci.log`
- `_logs/check_sins.log`
- `_logs/coverage.log`
- `_logs/validate_seed.log`
- `_logs/validate_neg.log`
- `_logs/build.log`
- `_logs/repro_build.log`
- `_logs/golden_compare.log`
- `_logs/client_smoke.log`
- `_logs/determinism.log`
- `_logs/narrative_check.log`
- `_logs/coverage_gate.log`

## Status files (generated)
- `_logs/*.status`

## Report artifacts (generated)
- `_logs/build_report.json`
- `_logs/validate_seed_report.json`
- `_logs/validate_neg_report.json`

## Persistent docs/artifacts kept in git
- `docs/COVERAGE_REPORT.md`
- `docs/SINS_REPORT.md`
- `tools/fixtures/golden/*`
