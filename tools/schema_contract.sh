#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs _out
python3 tools/py/schema_contract.py \
  --db _out/authoring.db \
  --schema content/authoring/schema.sql \
  --contract docs/schema_contracts/authoring_schema_contract.json \
  --create-db | tee _logs/schema_contract.log
