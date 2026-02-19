#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]

WHITELIST = [
    "wt_client",
    "scripts",
    "README.md",
    "RELEASE_BUILD.md",
    "CHANGELOG.md",
    "requirements.txt",
    "pyproject.toml",
]

EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".wt_logs", ".wt_cli_tmp", "runtime", ".git"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".tmp"}


def _is_allowed(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    low = str(rel).lower()
    if "backup" in low and rel.suffix.lower() == ".zip":
        return False
    return True


def _iter_whitelist_files() -> list[Path]:
    out: list[Path] = []
    for item in WHITELIST:
        p = ROOT / item
        if not p.exists():
            continue
        if p.is_file():
            if _is_allowed(p):
                out.append(p)
            continue
        for ch in sorted(p.rglob("*")):
            if ch.is_file() and _is_allowed(ch):
                out.append(ch)
    return sorted(set(out))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="stage_clean.zip")
    ap.add_argument("--manifest", default="manifest.json")
    args = ap.parse_args()

    files = _iter_whitelist_files()
    out_zip = ROOT / args.out
    manifest_path = ROOT / args.manifest

    with ZipFile(out_zip, "w", compression=ZIP_DEFLATED) as zf:
        for p in files:
            rel = p.relative_to(ROOT).as_posix()
            zf.write(p, rel)

    entries = []
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        entries.append({"path": rel, "sha256": _sha256_file(p)})

    manifest = {
        "zip": out_zip.name,
        "zip_sha256": _sha256_file(out_zip),
        "files": entries,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_zip}")
    print(f"Wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
