#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs client/_out
python3 client/run_narrative_check.py | tee _logs/narrative_check.log
