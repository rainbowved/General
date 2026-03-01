# CI_PROBE_LOG

## Commands and key outputs

1. `python3 --version`
   - `Python 3.14.0`

2. `git --version`
   - `git version 2.43.0`

3. `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`
   - `3.45.1`

4. `sqlite3 --version`
   - `3.45.1 2024-01-30 16:01:20 e876e51a0ed5c5b3126f52e532044363a014bc594cfefa87ffb5b82257ccalt1 (64-bit)`

5. `rg --version`
   - `ripgrep 14.1.0`

6. `CI_LEVEL=probe PHASE_TARGET=0 bash tools/ci.sh`
   - Probe run completed.
   - Step statuses from output:
     - `check_sins=OK`
     - `schema_contract=OK`
     - `coverage=OK`
     - `validate_seed=OK`
     - `validate_neg=OK`
     - `build=OK`
     - `repro_build=OK`
     - `golden_compare=OK`
     - `client_smoke=OK`
     - `determinism=OK`
     - `narrative_check=OK`
     - `coverage_gate=OK`

## Notes
- Log contains only local command outputs from this environment.
- No secrets/tokens are included.
