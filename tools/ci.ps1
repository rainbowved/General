$ErrorActionPreference="Stop"
$CI_LEVEL = if ($env:CI_LEVEL) { $env:CI_LEVEL } else { "probe" }
$PHASE_TARGET = if ($env:PHASE_TARGET) { $env:PHASE_TARGET } else { "0" }

if (Test-Path "tools\py\ci.py") {
  $env:CI_LEVEL = $CI_LEVEL
  $env:PHASE_TARGET = $PHASE_TARGET
  python tools/py/ci.py
  exit $LASTEXITCODE
}

Write-Host "[ERROR] tools/py/ci.py is required for STACK_PYTHON"
exit 2
