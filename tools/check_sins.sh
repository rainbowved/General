#!/usr/bin/env bash
set -euo pipefail
mkdir -p _logs
log="_logs/check_sins.log"
: > "$log"

echo "== check_sins ==" | tee -a "$log"
if command -v dotnet >/dev/null 2>&1 && [ -f tools/src/CheckSins/CheckSins.csproj ]; then
  echo "[INFO] running C# CheckSins" | tee -a "$log"
  if dotnet run --project tools/src/CheckSins/CheckSins.csproj >> "$log" 2>&1; then
    echo "[PASS] check_sins csharp" | tee -a "$log"
    exit 0
  else
    echo "[FAIL] check_sins csharp" | tee -a "$log"
    exit 1
  fi
fi

echo "[WARN] dotnet unavailable; using python-stack bootstrap scanner" | tee -a "$log"
count=$(rg -n "@@BEGIN:B" docs/concept 2>/dev/null | wc -l | tr -d ' ')
echo "[METRIC] begin_blocks=$count" | tee -a "$log"
mapfile -t files < <(find tools client content docs -type f \
  \( -name '*.cs' -o -name '*.py' -o -name '*.ps1' -o -name '*.sh' -o -name '*.sql' \) \
  ! -path 'docs/concept/*' ! -path '_logs/*' ! -path 'tools/src/CheckSins/*' ! -name 'check_sins.sh' ! -name 'check_sins.ps1' 2>/dev/null)
if [ "${#files[@]}" -gt 0 ] && rg -n "Guid\.NewGuid|DateTime\.Now|new Random\(|\bfloat\b|\bdouble\b|\bREAL\b|\bNUMERIC\b" "${files[@]}" >> "$log" 2>&1; then
  echo "[FAIL] banned deterministic sins detected" | tee -a "$log"
  exit 1
fi

echo "[PASS] check_sins bootstrap" | tee -a "$log"
