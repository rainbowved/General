from __future__ import annotations

import json
import logging
import os
import re
import shutil
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional

from wt_client.core.migrations import apply_migrations_to_document


log = logging.getLogger("wt_client.save_store")


@dataclass
class SaveValidationError(Exception):
    problems: List[str]

    def __str__(self) -> str:  # pragma: no cover
        lines = ["Save validation failed:"]
        lines.extend([f"- {p}" for p in self.problems])
        return "\n".join(lines)


@dataclass
class SaveIOError(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


@dataclass(frozen=True)
class SaveLayout:
    # The directory that contains primary save JSON files (player/world/progress/inventory).
    save_dir: Path
    # Optional session directory (contains session.json)
    session_dir: Optional[Path]
    # Paths relative to the *root passed to SaveStore* (for roundtrip persistence).
    rel_player: str
    rel_world: str
    rel_progress: str
    rel_inventory: str
    rel_session: Optional[str]


def _json_load(path: Path) -> Any:
    txt = path.read_text(encoding="utf-8")
    return json.loads(txt)


def _json_dump(obj: Any) -> str:
    # Deterministic, human-friendly.
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _is_dir_with_required_files(d: Path) -> bool:
    return all((d / f).is_file() for f in ("player.json", "world.json", "progress.json", "inventory.json"))


def detect_save_layout(save_root: Path) -> SaveLayout:
    """Detect save layout based on the shipped demo save.

    Supports two common shapes:
    1) save_root/ (player.json, world.json, progress.json, inventory.json)
    2) save_root/save/ (player.json, ...) with optional save_root/session/session.json
    """
    save_root = save_root.resolve()
    if (save_root / "save").is_dir() and _is_dir_with_required_files(save_root / "save"):
        sdir = save_root / "save"
        sesdir = (save_root / "session") if (save_root / "session").is_dir() else None
        rel_prefix = "save/"
        rel_session = "session/session.json" if (sesdir and (sesdir / "session.json").is_file()) else None
        return SaveLayout(
            save_dir=sdir,
            session_dir=sesdir,
            rel_player=rel_prefix + "player.json",
            rel_world=rel_prefix + "world.json",
            rel_progress=rel_prefix + "progress.json",
            rel_inventory=rel_prefix + "inventory.json",
            rel_session=rel_session,
        )

    # Flat root.
    if _is_dir_with_required_files(save_root):
        rel_session = "session.json" if (save_root / "session.json").is_file() else None
        return SaveLayout(
            save_dir=save_root,
            session_dir=save_root,
            rel_player="player.json",
            rel_world="world.json",
            rel_progress="progress.json",
            rel_inventory="inventory.json",
            rel_session=rel_session,
        )

    # Not detected.
    missing: List[str] = []
    for f in ("player.json", "world.json", "progress.json", "inventory.json"):
        if not (save_root / f).exists() and not (save_root / "save" / f).exists():
            missing.append(f)
    raise SaveValidationError(
        [
            f"Not a recognized save directory: {save_root}",
            "Expected either:",
            "  - <save_dir>/{player,world,progress,inventory}.json",
            "  - <save_dir>/save/{player,world,progress,inventory}.json (demo layout)",
            f"Missing required files: {', '.join(missing) if missing else '(unknown)'}",
        ]
    )


def _timestamp_utc() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.gmtime())


def _safe_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix().lstrip("/")


def _validate_top(doc: Any, *, name: str, required: Dict[str, type], problems: List[str]) -> Optional[MutableMapping]:
    if not isinstance(doc, dict):
        problems.append(f"{name}: expected JSON object, got {type(doc).__name__}")
        return None
    for k, t in required.items():
        if k not in doc:
            problems.append(f"{name}: missing required field '{k}'")
        else:
            if not isinstance(doc[k], t):
                problems.append(f"{name}: field '{k}' expected {t.__name__}, got {type(doc[k]).__name__}")
    return doc


class SaveStore:
    """Load/save GameState from a save directory.

    Notes:
    - crash-safe writes: write to temp dir, then swap into place
    - rolling backups: keep last N zipped snapshots
    - micro-migrations: normalize missing runtime sections (cursor/recent_actions)
    """

    REQUIRED_SAVE_FIELDS: Dict[str, type] = {
        "schema_version": str,
        "save_id": str,
        "created_ts": str,
        "updated_ts": str,
    }
    REQUIRED_SAVE_FIELDS_WITH_PACK: Dict[str, type] = {
        **REQUIRED_SAVE_FIELDS,
        "pack_version": str,
    }
    REQUIRED_SESSION_FIELDS: Dict[str, type] = {
        "schema_version": str,
        "save_id": str,
        "session_id": str,
        "created_ts": str,
    }

    BACKUPS_DIRNAME = "backups"
    TMP_DIR_BASENAME = ".save_tmp"
    DEFAULT_ROLLING_BACKUPS = 10
    SUPPORTED_SCHEMA_MAJOR = 0
    SUPPORTED_SCHEMA_MINOR = 6

    def load_save(self, save_dir: str | Path) -> Dict[str, Any]:
        root = Path(save_dir).expanduser()
        if not root.exists() or not root.is_dir():
            raise SaveValidationError([f"Save directory does not exist or is not a directory: {root}"])

        layout = detect_save_layout(root)
        problems: List[str] = []

        # Load primary documents.
        p_player = root / layout.rel_player
        p_world = root / layout.rel_world
        p_progress = root / layout.rel_progress
        p_inventory = root / layout.rel_inventory

        try:
            player = _json_load(p_player)
        except Exception as e:
            problems.append(f"player.json: failed to load JSON: {e}")
            player = None
        try:
            world = _json_load(p_world)
        except Exception as e:
            problems.append(f"world.json: failed to load JSON: {e}")
            world = None
        try:
            progress = _json_load(p_progress)
        except Exception as e:
            problems.append(f"progress.json: failed to load JSON: {e}")
            progress = None
        try:
            inventory = _json_load(p_inventory)
        except Exception as e:
            problems.append(f"inventory.json: failed to load JSON: {e}")
            inventory = None

        player = _validate_top(player, name="player.json", required=self.REQUIRED_SAVE_FIELDS_WITH_PACK, problems=problems)
        world = _validate_top(world, name="world.json", required=self.REQUIRED_SAVE_FIELDS_WITH_PACK, problems=problems)
        progress = _validate_top(progress, name="progress.json", required=self.REQUIRED_SAVE_FIELDS_WITH_PACK, problems=problems)
        inventory = _validate_top(inventory, name="inventory.json", required=self.REQUIRED_SAVE_FIELDS_WITH_PACK, problems=problems)

        session: Optional[MutableMapping] = None
        if layout.rel_session:
            p_session = root / layout.rel_session
            try:
                sess = _json_load(p_session)
            except Exception as e:
                problems.append(f"session.json: failed to load JSON: {e}")
                sess = None
            session = _validate_top(sess, name="session.json", required=self.REQUIRED_SESSION_FIELDS, problems=problems)

        if problems:
            raise SaveValidationError(problems)

        # Compatibility check (clear UX for too-new/too-old saves).
        self._check_schema_compatibility(
            player.get("schema_version"),
            context="player.schema_version",
        )

        # Cross-file consistency checks.
        save_ids = {d["save_id"] for d in (player, world, progress, inventory) if d is not None}
        if session is not None:
            save_ids.add(session["save_id"])
        if len(save_ids) != 1:
            raise SaveValidationError([f"save_id mismatch across documents: {sorted(save_ids)}"])
        save_id = next(iter(save_ids))

        pack_versions = {d.get("pack_version") for d in (player, world, progress, inventory) if isinstance(d, dict)}
        pack_versions.discard(None)
        pack_version = next(iter(pack_versions)) if len(pack_versions) == 1 else None

        # Apply migrations skeleton (no-op unless registry is populated).
        mig_warnings: List[str] = []
        mig_steps: List[str] = []
        for label, doc in ("player", player), ("world", world), ("progress", progress), ("inventory", inventory):
            assert doc is not None
            new_doc, rep = apply_migrations_to_document(doc, label=label + ":")
            mig_warnings.extend(rep.warnings)
            mig_steps.extend(rep.steps)
            if label == "player":
                player = new_doc
            elif label == "world":
                world = new_doc
            elif label == "progress":
                progress = new_doc
            else:
                inventory = new_doc
        if session is not None:
            session, rep = apply_migrations_to_document(session, label="session:")
            mig_warnings.extend(rep.warnings)
            mig_steps.extend(rep.steps)

        # Extras: preserve any additional files under root (outside the core documents).
        extras_bytes: Dict[str, bytes] = {}
        core_rel = {layout.rel_player, layout.rel_world, layout.rel_progress, layout.rel_inventory}
        if layout.rel_session:
            core_rel.add(layout.rel_session)
        for p in [x for x in root.rglob("*") if x.is_file()]:
            rel = _safe_rel(p, root)
            if rel in core_rel:
                continue
            # Internal folders should not be treated as save-state extras.
            if rel.startswith(self.BACKUPS_DIRNAME + "/"):
                continue
            if rel.startswith(self.TMP_DIR_BASENAME + "/"):
                continue
            extras_bytes[rel] = p.read_bytes()

        state: Dict[str, Any] = {
            "meta": {
                "save_id": save_id,
                "pack_version": pack_version,
                "schema_versions": {
                    "player": player.get("schema_version"),
                    "world": world.get("schema_version"),
                    "progress": progress.get("schema_version"),
                    "inventory": inventory.get("schema_version"),
                    "session": session.get("schema_version") if session else None,
                },
                "layout": {
                    "rel_player": layout.rel_player,
                    "rel_world": layout.rel_world,
                    "rel_progress": layout.rel_progress,
                    "rel_inventory": layout.rel_inventory,
                    "rel_session": layout.rel_session,
                },
                "migration": {
                    "steps": mig_steps,
                    "warnings": mig_warnings,
                },
            },
            "player": player,
            "world": world,
            "progress": progress,
            "inventory": inventory,
            "session": session,
            "extras": extras_bytes,
        }

        self._normalize_runtime_sections(state)
        return state

    def _check_schema_compatibility(self, schema_version: Any, *, context: str) -> None:
        if not isinstance(schema_version, str):
            return
        m = re.match(r"^(\d+)\.(\d+)", schema_version.strip())
        if not m:
            return
        major = int(m.group(1))
        minor = int(m.group(2))
        exp = (self.SUPPORTED_SCHEMA_MAJOR, self.SUPPORTED_SCHEMA_MINOR)
        got = (major, minor)
        if got == exp:
            return
        if got > exp:
            raise SaveValidationError(
                [
                    f"Save is too new for this client ({context}={schema_version}).",
                    f"Supported: {exp[0]}.{exp[1]}.*",
                ]
            )
        raise SaveValidationError(
            [
                f"Save is too old for this client ({context}={schema_version}).",
                f"Supported: {exp[0]}.{exp[1]}.*",
            ]
        )

    def save_save(
        self,
        save_dir: str | Path,
        state: Dict[str, Any],
        *,
        create_backup: bool = True,
        rolling_backups: int = DEFAULT_ROLLING_BACKUPS,
    ) -> Optional[Path]:
        """Crash-safe save write + rolling backup.

        Writes state into a temp folder, then swaps it into place. Optionally creates
        a zipped backup under <save_dir>/backups/.
        """
        root = Path(save_dir).expanduser().resolve()
        root.parent.mkdir(parents=True, exist_ok=True)
        root.mkdir(parents=True, exist_ok=True)

        self._normalize_runtime_sections(state)

        tmp_root = root.parent / f"{self.TMP_DIR_BASENAME}_{root.name}_{os.getpid()}_{time.time_ns()}"
        # NOTE: never use a fixed .bak directory for swaps. On Windows, replacing an existing
        # directory target is error-prone; we also want to avoid overwriting recovery artifacts.
        bak_root = self._alloc_swap_backup_root(root)

        try:
            if tmp_root.exists():
                shutil.rmtree(tmp_root)
            tmp_root.mkdir(parents=True, exist_ok=True)

            # Preserve existing backups across atomic directory swaps.
            try:
                old_bdir = root / self.BACKUPS_DIRNAME
                if old_bdir.exists() and old_bdir.is_dir():
                    shutil.copytree(old_bdir, tmp_root / self.BACKUPS_DIRNAME)
            except Exception:
                # Backups are best-effort; do not block saving.
                pass

            self._write_save_tree(tmp_root, state)
            self._atomic_swap_dirs(root, tmp_root, bak_root)

            if create_backup:
                bp = self._create_backup_from_disk(root, state=state, rolling_backups=rolling_backups)
                return bp
            return None
        except SaveIOError:
            raise
        except Exception as e:
            log.exception("save failed")
            raise SaveIOError(f"Save failed: {e}")
        finally:
            # Best-effort cleanup of stale swap artifacts from previous crashes.
            # Never throw here.
            try:
                self._cleanup_orphaned_swap_artifacts(root)
            except Exception:
                pass
            try:
                if tmp_root.exists():
                    shutil.rmtree(tmp_root)
            except Exception:
                pass

    # --- backups / restore ---
    def list_backups(self, save_dir: str | Path) -> List[Path]:
        root = Path(save_dir).expanduser().resolve()
        bdir = root / self.BACKUPS_DIRNAME
        if not bdir.exists() or not bdir.is_dir():
            return []
        items = [p for p in bdir.iterdir() if p.is_file() and p.suffix.lower() == ".zip"]
        return sorted(items, key=lambda p: p.name)

    def restore_backup(self, save_dir: str | Path, backup_path: str | Path) -> None:
        root = Path(save_dir).expanduser().resolve()
        bp = Path(backup_path).expanduser().resolve()
        if not bp.exists() or not bp.is_file():
            raise SaveIOError(f"Backup does not exist: {bp}")

        tmp_root = root.parent / f"{self.TMP_DIR_BASENAME}_restore_{root.name}_{os.getpid()}_{time.time_ns()}"
        bak_root = self._alloc_swap_backup_root(root)

        try:
            if tmp_root.exists():
                shutil.rmtree(tmp_root)
            tmp_root.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(str(bp), "r") as z:
                z.extractall(str(tmp_root))

            # Preserve existing backups across restore.
            try:
                old_bdir = root / self.BACKUPS_DIRNAME
                if old_bdir.exists() and old_bdir.is_dir() and not (tmp_root / self.BACKUPS_DIRNAME).exists():
                    shutil.copytree(old_bdir, tmp_root / self.BACKUPS_DIRNAME)
            except Exception:
                pass

            _ = detect_save_layout(tmp_root)
            self._atomic_swap_dirs(root, tmp_root, bak_root)
        except SaveValidationError as e:
            raise SaveIOError(str(e))
        except SaveIOError:
            raise
        except Exception as e:
            log.exception("restore failed")
            raise SaveIOError(f"Restore failed: {e}")
        finally:
            try:
                self._cleanup_orphaned_swap_artifacts(root)
            except Exception:
                pass
            try:
                if tmp_root.exists():
                    shutil.rmtree(tmp_root)
            except Exception:
                pass

    # --- internals ---
    def _normalize_runtime_sections(self, state: Dict[str, Any]) -> None:
        """Micro-migrations (safe, no mechanics).

        Ensures:
        - progress is a dict
        - cursor exists for idempotency
        - progress.recent_actions is a list
        """
        prog = state.get("progress")
        if not isinstance(prog, dict):
            prog = {}
            state["progress"] = prog

        ses = state.get("session")
        container = ses if isinstance(ses, dict) else prog

        cur = container.get("cursor") if isinstance(container, dict) else None
        if not isinstance(cur, dict):
            container["cursor"] = {"schema": "cursor_v1", "max_size": 10000, "seen_event_ids": [], "seen_hash": ""}
        else:
            if not isinstance(cur.get("seen_event_ids"), list):
                cur["seen_event_ids"] = []
            if not isinstance(cur.get("seen_hash"), str):
                cur["seen_hash"] = ""
            if "max_size" not in cur:
                cur["max_size"] = 10000
            if "schema" not in cur:
                cur["schema"] = "cursor_v1"

        if not isinstance(prog.get("recent_actions"), list):
            prog["recent_actions"] = []

    def _write_save_tree(self, root: Path, state: Dict[str, Any]) -> None:
        meta = state.get("meta") or {}
        layout_info = (meta.get("layout") or {})

        rel_player = layout_info.get("rel_player") or "player.json"
        rel_world = layout_info.get("rel_world") or "world.json"
        rel_progress = layout_info.get("rel_progress") or "progress.json"
        rel_inventory = layout_info.get("rel_inventory") or "inventory.json"
        rel_session = layout_info.get("rel_session")

        def _write_json(rel: str, obj: Any) -> None:
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(_json_dump(obj), encoding="utf-8")

        try:
            _write_json(rel_player, state["player"])
            _write_json(rel_world, state["world"])
            _write_json(rel_progress, state["progress"])
            _write_json(rel_inventory, state["inventory"])
            if rel_session and state.get("session") is not None:
                _write_json(rel_session, state["session"])
        except KeyError as e:
            raise SaveIOError(f"Save failed: missing state section {e}")

        extras: Dict[str, bytes] = state.get("extras") or {}
        for rel, blob in extras.items():
            if rel.startswith(self.BACKUPS_DIRNAME + "/") or rel.startswith(self.TMP_DIR_BASENAME + "/"):
                continue
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)

    def _atomic_swap_dirs(self, dst_root: Path, tmp_root: Path, bak_root: Path) -> None:
        """Swap tmp_root into dst_root.

        This is designed so that a crash never leaves a half-written save:
        - writes happen only in tmp_root
        - old save is moved aside first, then tmp replaces it
        - if swap fails, attempt rollback
        """
        dst_root.parent.mkdir(parents=True, exist_ok=True)
        dst_root = dst_root.resolve()
        tmp_root = tmp_root.resolve()
        bak_root = bak_root.resolve()

        # Windows-safe directory swap algorithm:
        # 1) dst_root -> unique bak_root (only if dst exists)
        # 2) tmp_root -> dst_root (dst must not exist)
        # 3) cleanup bak_root (best-effort)
        # If step 2 fails, rollback bak_root -> dst_root.
        moved_old = False
        try:
            if dst_root.exists():
                # bak_root MUST NOT exist.
                if bak_root.exists():
                    raise SaveIOError(f"Save failed during atomic swap: swap backup already exists: {bak_root}")
                os.replace(str(dst_root), str(bak_root))
                moved_old = True

            # At this point dst_root should not exist.
            if dst_root.exists():
                raise SaveIOError(f"Save failed during atomic swap: destination still exists after move: {dst_root}")

            os.replace(str(tmp_root), str(dst_root))
        except SaveIOError:
            raise
        except Exception as e:
            # rollback best-effort
            try:
                if moved_old and (not dst_root.exists()) and bak_root.exists():
                    os.replace(str(bak_root), str(dst_root))
            except Exception:
                pass
            raise SaveIOError(f"Save failed during atomic swap: {e}")
        finally:
            # drop old copy if swap succeeded; if it fails, keep it for manual recovery.
            try:
                if bak_root.exists():
                    shutil.rmtree(bak_root)
            except Exception:
                pass

    def _alloc_swap_backup_root(self, dst_root: Path) -> Path:
        """Allocate a unique swap-backup folder path.

        This is *not* the rolling backups feature. This is only a temporary safety net
        during an atomic directory swap.
        """
        parent = dst_root.parent
        base = f".{dst_root.name}.swapbak_{_timestamp_utc()}_{os.getpid()}_{time.time_ns()}"
        out = parent / base
        seq = 0
        while out.exists():
            seq += 1
            out = parent / f"{base}_{seq:03d}"
        return out

    def _cleanup_orphaned_swap_artifacts(self, dst_root: Path, *, max_age_seconds: int = 24 * 3600) -> None:
        """Best-effort cleanup for orphaned temp/backup dirs from previous crashes.

        We only remove items older than max_age_seconds to avoid interfering with a
        concurrent process.
        """
        parent = dst_root.parent
        name = dst_root.name
        now = time.time()

        patterns = [
            f"{self.TMP_DIR_BASENAME}_{name}_*",
            f"{self.TMP_DIR_BASENAME}_restore_{name}_*",
            f".{name}.swapbak_*",
        ]

        for pat in patterns:
            for p in parent.glob(pat):
                try:
                    if not p.is_dir():
                        continue
                    age = now - p.stat().st_mtime
                    if age < max_age_seconds:
                        continue
                    shutil.rmtree(p)
                except Exception:
                    pass

    def _create_backup_from_disk(self, root: Path, *, state: Dict[str, Any], rolling_backups: int) -> Path:
        bdir = root / self.BACKUPS_DIRNAME
        bdir.mkdir(parents=True, exist_ok=True)

        # Cursor marker for filename.
        cursor_n = 0
        try:
            cur = None
            ses = state.get("session")
            if isinstance(ses, dict) and isinstance(ses.get("cursor"), dict):
                cur = ses.get("cursor")
            prog = state.get("progress")
            if cur is None and isinstance(prog, dict) and isinstance(prog.get("cursor"), dict):
                cur = prog.get("cursor")
            if isinstance(cur, dict) and isinstance(cur.get("seen_event_ids"), list):
                cursor_n = len(cur.get("seen_event_ids") or [])
        except Exception:
            cursor_n = 0

        ts = _timestamp_utc()
        base = f"{ts}_cursor{cursor_n:06d}"
        seq = 0
        while True:
            out = bdir / f"{base}_{seq:03d}.zip"
            if not out.exists():
                break
            seq += 1

        with zipfile.ZipFile(str(out), "w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                rel = _safe_rel(p, root)
                if rel.startswith(self.BACKUPS_DIRNAME + "/"):
                    continue
                if rel.startswith(self.TMP_DIR_BASENAME + "/"):
                    continue
                z.write(str(p), arcname=rel)

        try:
            rolling_backups = int(rolling_backups)
        except Exception:
            rolling_backups = self.DEFAULT_ROLLING_BACKUPS
        rolling_backups = max(1, min(rolling_backups, 200))

        items = sorted([p for p in bdir.iterdir() if p.is_file() and p.suffix.lower() == ".zip"], key=lambda p: p.name)
        if len(items) > rolling_backups:
            for p in items[: len(items) - rolling_backups]:
                try:
                    p.unlink()
                except Exception:
                    pass

        return out
