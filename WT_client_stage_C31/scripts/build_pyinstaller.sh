#!/usr/bin/env bash
set -euo pipefail

python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller --noconfirm --clean \
  --name wt_client \
  --collect-all wt_client \
  -m wt_client

echo "Built: dist/wt_client/wt_client"
