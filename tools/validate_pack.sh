#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs
if [ "${1:-}" = "--seed" ]; then
  python3 tools/py/validate_pack.py --seed --emit-report _logs/validate_seed_report.json --compare-golden tools/fixtures/golden/validate_expected.json | tee _logs/validate_seed.log
elif [ "${1:-}" = "--neg" ]; then
  python3 tools/py/validate_pack.py --neg --emit-report _logs/validate_neg_report.json | tee _logs/validate_neg.log
else
  echo "usage: $0 --seed|--neg"; exit 2
fi
