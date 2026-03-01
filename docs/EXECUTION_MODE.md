# EXECUTION MODE

- **Mode:** MODE A (FS + terminal + runtime available)
- **Stack:** STACK_PYTHON
- **Decision basis:** `dotnet` is unavailable, `python3` is available, terminal execution is available, zip unpack/pack works.

## Fallback plan
1. If Python runtime fails in later phases, degrade to `STACK_GENERATE_ONLY` and mark all runtime gates as `UNVERIFIED`.
2. If any mandatory command cannot be executed in this environment, log exact command + expected output in `docs/LOCAL_RUN_INSTRUCTIONS.md` and keep status fail-closed.
3. Keep CI scripts mode-aware (`probe` first in PHASE 0, then `full` from PHASE 2+) per prompt requirements.
