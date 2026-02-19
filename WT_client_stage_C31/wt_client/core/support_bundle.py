from __future__ import annotations

import json
import logging
import os
import platform
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


log = logging.getLogger("wt_client.support")


def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _redact_path(p: str) -> str:
    """Best-effort path redaction: remove user names from common home dirs."""
    s = str(p)
    try:
        home = str(Path.home())
        if home and s.startswith(home):
            s = "~" + s[len(home) :]
    except Exception:
        pass

    # Windows: C:\Users\<name>\...
    s = re.sub(r"(?i)\\Users\\[^\\]+", r"\\Users\\_", s)
    # macOS: /Users/<name>/...
    s = re.sub(r"/Users/[^/]+", r"/Users/_", s)
    # Linux: /home/<name>/...
    s = re.sub(r"/home/[^/]+", r"/home/_", s)
    return s


def _cursor_summary(state: Mapping[str, Any]) -> Dict[str, Any]:
    ses = state.get("session")
    prog = state.get("progress")
    cur = None
    if isinstance(ses, dict) and isinstance(ses.get("cursor"), dict):
        cur = ses.get("cursor")
    if cur is None and isinstance(prog, dict) and isinstance(prog.get("cursor"), dict):
        cur = prog.get("cursor")
    if not isinstance(cur, dict):
        return {"seen_event_ids_count": 0, "seen_hash": ""}
    ids = cur.get("seen_event_ids")
    if not isinstance(ids, list):
        ids = []
    h = cur.get("seen_hash")
    return {"seen_event_ids_count": len(ids), "seen_hash": str(h or "")}


def _extract_seed(state: Mapping[str, Any]) -> str:
    rng = state.get("rng")
    if isinstance(rng, dict):
        ms = rng.get("master_seed")
        if isinstance(ms, str) and ms:
            return ms
        seeds = rng.get("seeds")
        if isinstance(seeds, dict):
            for k in ("run_seed", "world_seed"):
                v = seeds.get(k)
                if isinstance(v, str) and v:
                    return v
    # Legacy spots (best-effort)
    meta = state.get("meta")
    if isinstance(meta, dict):
        v = meta.get("seed")
        if isinstance(v, str) and v:
            return v
    return ""


def _extract_pack_id(state: Mapping[str, Any], *, pack_path: str) -> str:
    meta = state.get("meta")
    if isinstance(meta, dict):
        for k in ("pack_id", "pack_version", "content_version"):
            v = meta.get(k)
            if isinstance(v, str) and v:
                return v
    # fallback: filename marker
    try:
        return Path(pack_path).name
    except Exception:
        return ""


def _add_dir_to_zip(
    zf: zipfile.ZipFile,
    src_dir: Path,
    *,
    arc_prefix: str,
    exclude_regex: Optional[re.Pattern[str]] = None,
) -> int:
    added = 0
    if not src_dir.exists() or not src_dir.is_dir():
        return 0
    for p in sorted(src_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(src_dir).as_posix()
        if exclude_regex and exclude_regex.search(rel):
            continue
        arc = f"{arc_prefix.rstrip('/')}/{rel}" if arc_prefix else rel
        zf.write(p, arcname=arc)
        added += 1
    return added


def _write_json_to_zip(zf: zipfile.ZipFile, arcname: str, obj: Any) -> None:
    data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    zf.writestr(arcname, data)


@dataclass(frozen=True)
class SupportBundleResult:
    path: Path
    files_added: int
    message: str


def create_support_bundle(
    *,
    logs_dir: str | Path,
    save_dir: str | Path,
    pack_path: str,
    state: Mapping[str, Any],
    out_path: Optional[str | Path] = None,
) -> SupportBundleResult:
    """Create a support ZIP for bug reports.

    Contains:
      - logs (latest files from logs_dir, excluding nested support bundles)
      - last exported TURNPACK (if tracked in logs_dir/last_turnpack.json)
      - minimal save meta: cursor summary, seed, pack id
      - technical runtime info (versions/paths)

    No full save contents are included.
    """

    logs_dir_p = Path(logs_dir).expanduser().resolve()
    save_dir_p = Path(save_dir).expanduser().resolve()

    # Default output location
    if out_path is None:
        out_root = logs_dir_p / "support_bundles"
        out_root.mkdir(parents=True, exist_ok=True)
        out_zip = out_root / f"support_bundle_{_utc_now_compact()}_{os.getpid()}.zip"
    else:
        out_zip = Path(out_path).expanduser().resolve()
        out_zip.parent.mkdir(parents=True, exist_ok=True)

    last_turnpack = logs_dir_p / "last_turnpack.json"
    last_turnpack_present = last_turnpack.exists() and last_turnpack.is_file()

    meta: Dict[str, Any] = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "client": {
            "python": sys.version.split("\n")[0],
            "platform": platform.platform(),
        },
        "paths": {
            "pack_path": _redact_path(pack_path),
            "save_dir": _redact_path(str(save_dir_p)),
            "logs_dir": _redact_path(str(logs_dir_p)),
        },
        "save_meta": {
            "cursor": _cursor_summary(state),
            "seed": _extract_seed(state),
            "pack_id": _extract_pack_id(state, pack_path=pack_path),
        },
        "artifacts": {
            "last_turnpack_present": bool(last_turnpack_present),
        },
    }

    files_added = 0
    try:
        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            _write_json_to_zip(zf, "meta/support_meta.json", meta)
            files_added += 1

            # Logs (exclude recursive bundles + explicit last_turnpack.json to avoid duplication)
            exclude = re.compile(r"(^|/)(support_bundles/|last_turnpack\.json$)")
            files_added += _add_dir_to_zip(zf, logs_dir_p, arc_prefix="logs", exclude_regex=exclude)

            if last_turnpack_present:
                zf.write(last_turnpack, arcname="turnpack/last_turnpack.json")
                files_added += 1

            # Minimal save slot marker (path only, redacted); no files.
            _write_json_to_zip(
                zf,
                "meta/save_slot.json",
                {"save_dir": _redact_path(str(save_dir_p))},
            )
            files_added += 1

        return SupportBundleResult(path=out_zip, files_added=files_added, message="ok")
    except Exception as e:
        log.exception("support bundle failed")
        # Ensure no half-written file is left around.
        try:
            if out_zip.exists():
                out_zip.unlink()
        except Exception:
            pass
        raise RuntimeError(f"support bundle failed: {e}")
