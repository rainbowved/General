# WT RPG Client — release build (C19)

This stage adds a **reproducible, documented build** for a portable Windows/macOS/Linux client.

## Prereqs

- Python 3.11+ recommended
- `pip` available

Install runtime deps:

```bash
python -m pip install -r requirements.txt
```

## Portable data layout

By default, the client uses **relative** paths (portable mode):

- `./WT_data_release_candidate.zip` (datapack)
- `./saves/` (save slots)
- `./.wt_logs/` (logs; tracebacks only here)

Override the data root with:

```bash
set WT_DATA_ROOT=D:\WT\userdata   # Windows
export WT_DATA_ROOT=~/WT/userdata   # macOS/Linux
```

## PyInstaller (recommended)

Install:

```bash
python -m pip install pyinstaller
```

Build (Windows PowerShell):

```powershell
./scripts/build_pyinstaller.ps1
```

Build (macOS/Linux):

```bash
./scripts/build_pyinstaller.sh
```

Output:

- `dist/wt_client/wt_client.exe` (Windows) or `dist/wt_client/wt_client` (macOS/Linux)

## Runtime

Place the datapack near the executable (or set `WT_DATA_ROOT`). Then run:

```bash
wt_client --ui
```
