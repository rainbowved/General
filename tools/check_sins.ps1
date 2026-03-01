$ErrorActionPreference="Stop"
New-Item -ItemType Directory -Force -Path _logs | Out-Null
python tools/py/check_sins.py --report docs/SINS_REPORT.md *>&1 | Tee-Object -FilePath "_logs/check_sins.log"
exit $LASTEXITCODE
