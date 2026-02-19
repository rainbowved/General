$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller --noconfirm --clean `
  --name wt_client `
  --collect-all wt_client `
  -m wt_client

Write-Host "Built: dist/wt_client/wt_client.exe"
