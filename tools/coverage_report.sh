#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs
python3 tools/py/coverage_report.py | tee _logs/coverage.log
