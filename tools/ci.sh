#!/usr/bin/env bash
set -euo pipefail

CI_LEVEL="${CI_LEVEL:-probe}"
PHASE_TARGET="${PHASE_TARGET:-0}"

if [ -f tools/py/ci.py ]; then
  CI_LEVEL="$CI_LEVEL" PHASE_TARGET="$PHASE_TARGET" python3 tools/py/ci.py
  exit $?
fi

echo "[ERROR] tools/py/ci.py is required for STACK_PYTHON"
exit 2
