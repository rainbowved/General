#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs tools/fixtures/golden

if [ "${ACCEPT_GOLDEN:-0}" != "1" ] && [ "${1:-}" != "--accept-golden" ]; then
  echo "[ERROR] golden update denied. Use --accept-golden or ACCEPT_GOLDEN=1" | tee _logs/update_golden.log
  exit 2
fi

echo "[INFO] updating validate golden" | tee _logs/update_golden.log
python3 tools/py/validate_pack.py --seed --emit-report /tmp/validate_seed_new.json >/dev/null
cp /tmp/validate_seed_new.json tools/fixtures/golden/validate_expected.json

echo "[INFO] updating build golden" | tee -a _logs/update_golden.log
python3 tools/py/build_pack.py --emit-report /tmp/build_new.json >/dev/null
cp /tmp/build_new.json tools/fixtures/golden/build_expected.json
cp content/dist/v0.1.0/sha256.txt tools/fixtures/golden/content_db_sha256.txt

echo "[PASS] golden updated" | tee -a _logs/update_golden.log
