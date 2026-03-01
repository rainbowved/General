#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs docs
python3 tools/py/check_sins.py --report docs/SINS_REPORT.md | tee _logs/check_sins.log
