#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs client/_out
python3 client/run_determinism.py | tee _logs/determinism.log
