#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs client/_out
python3 client/run_smoke.py | tee _logs/client_smoke.log
