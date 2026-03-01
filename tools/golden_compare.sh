#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs
python3 tools/py/golden_compare.py | tee _logs/golden_compare.log
