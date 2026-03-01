$ErrorActionPreference="Stop"
New-Item -ItemType Directory -Force -Path _logs | Out-Null
$log="_logs/check_sins.log"
"== check_sins ==" | Out-File -Encoding utf8 -FilePath $log

if ((Get-Command dotnet -ErrorAction SilentlyContinue) -and (Test-Path "tools/src/CheckSins/CheckSins.csproj")) {
  "[INFO] running C# CheckSins" | Tee-Object -FilePath $log -Append | Out-Null
  dotnet run --project tools/src/CheckSins/CheckSins.csproj *>> $log
  if ($LASTEXITCODE -eq 0) {
    "[PASS] check_sins csharp" | Tee-Object -FilePath $log -Append | Out-Null
    exit 0
  }
  "[FAIL] check_sins csharp" | Tee-Object -FilePath $log -Append | Out-Null
  exit 1
}

"[WARN] dotnet unavailable; using python-stack bootstrap scanner" | Tee-Object -FilePath $log -Append | Out-Null
$beginCount = 0
if (Test-Path "docs/concept") {
  $beginCount = (Select-String -Path "docs/concept/*" -Pattern "@@BEGIN:B" -SimpleMatch -ErrorAction SilentlyContinue | Measure-Object).Count
}
"[METRIC] begin_blocks=$beginCount" | Tee-Object -FilePath $log -Append | Out-Null
$targets = @("tools","client","content","docs") | Where-Object { Test-Path $_ }
$hits = @()
foreach ($t in $targets) {
  $hits += Select-String -Path "$t/*" -Pattern "Guid.NewGuid|DateTime.Now|new Random\(|\bfloat\b|\bdouble\b|\bREAL\b|\bNUMERIC\b" -Recurse -ErrorAction SilentlyContinue
}
$hits = $hits | Where-Object { $_.Path -notmatch "docs\\concept|\\.git\\|\\_logs\\|check_sins\\.ps1|check_sins\\.sh" }
if ($hits) {
  $hits | ForEach-Object { $_.ToString() } | Tee-Object -FilePath $log -Append | Out-Null
  "[FAIL] banned deterministic sins detected" | Tee-Object -FilePath $log -Append | Out-Null
  exit 1
}
"[PASS] check_sins bootstrap" | Tee-Object -FilePath $log -Append | Out-Null
