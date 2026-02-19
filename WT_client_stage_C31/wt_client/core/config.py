from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AppConfig:
    datapack_path: str
    save_root: str
    logs_dir: str

    @staticmethod
    def defaults() -> "AppConfig":
        # Portable defaults:
        # - Prefer relative paths so the client can run from an extracted folder.
        # - Avoid writing into package directories that may be read-only (Program Files).
        base = default_data_root()
        return AppConfig(
            datapack_path=str(base / "WT_data_release_candidate.zip"),
            save_root=str(base / "saves"),
            logs_dir=str(base / ".wt_logs"),
        )

    @staticmethod
    def load(path: Optional[str]) -> "AppConfig":
        if not path:
            return AppConfig.defaults()
        p = Path(path)
        if not p.exists():
            return AppConfig.defaults()
        data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
        base = AppConfig.defaults()
        return AppConfig(
            datapack_path=str(data.get("datapack_path", base.datapack_path)),
            save_root=str(data.get("save_root", base.save_root)),
            logs_dir=str(data.get("logs_dir", base.logs_dir)),
        )


def resolve_repo_config_path() -> Optional[str]:
    """Try to locate ./wt_client/config.json relative to current working directory."""
    p = Path.cwd() / "wt_client" / "config.json"
    return str(p) if p.exists() else None


def default_data_root() -> Path:
    """Return a portable writable directory for saves/logs.

    Strategy:
      1) If WT_DATA_ROOT is set, use it.
      2) If running as a frozen executable, place data next to the .exe.
      3) Otherwise, use current working directory.
    """

    env = os.environ.get("WT_DATA_ROOT")
    if env:
        return Path(env).expanduser().resolve()

    # PyInstaller / frozen app: keep data near the executable (portable mode).
    if getattr(sys, "frozen", False):
        try:
            return Path(sys.executable).resolve().parent
        except Exception:
            pass

    return Path.cwd().resolve()
