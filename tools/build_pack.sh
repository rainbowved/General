#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs
if [ "${1:-}" = "--repro" ]; then
  python3 tools/py/build_pack.py --repro --emit-report _logs/build_report.json --compare-golden tools/fixtures/golden/build_expected.json | tee _logs/repro_build.log
else
  python3 tools/py/build_pack.py --emit-report _logs/build_report.json --compare-golden tools/fixtures/golden/build_expected.json | tee _logs/build.log
fi
