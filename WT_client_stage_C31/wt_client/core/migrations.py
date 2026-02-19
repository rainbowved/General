from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from typing import Callable, Dict, List, MutableMapping, Tuple

log = logging.getLogger("wt_client.migrations")
MigrationFn = Callable[[MutableMapping], Tuple[MutableMapping, List[str]]]


@dataclass
class MigrationReport:
    changed: bool
    steps: List[str]
    warnings: List[str]


def _migrate_cursor_to_session(doc: MutableMapping) -> Tuple[MutableMapping, List[str]]:
    out = copy.deepcopy(doc)
    warnings: List[str] = []
    legacy = out.pop("cursor", None)
    ses = out.setdefault("session", {})
    if isinstance(legacy, dict) and isinstance(ses, dict) and "cursor" not in ses:
        ses["cursor"] = legacy
    out["schema_version"] = "0.6.4-save1"
    return out, warnings


def _migrate_normalize_meters(doc: MutableMapping) -> Tuple[MutableMapping, List[str]]:
    out = copy.deepcopy(doc)
    warnings: List[str] = []
    pl = out.setdefault("player", {})
    meters = pl.setdefault("meters", {}) if isinstance(pl, dict) else {}
    if isinstance(meters, dict):
        for key in ("fat_current", "fat_max_cached", "hunger", "thirst"):
            v = meters.get(key, 0)
            try:
                iv = int(v)
            except Exception:
                iv = 0
            meters[key] = max(0, min(100, iv))
    out["schema_version"] = "0.6.5-save1"
    return out, warnings


MIGRATIONS: Dict[str, MigrationFn] = {
    "0.6.3-save1": _migrate_cursor_to_session,
    "0.6.4-save1": _migrate_normalize_meters,
}


def apply_migrations_to_document(doc: MutableMapping, *, label: str = "") -> Tuple[MutableMapping, MigrationReport]:
    steps: List[str] = []
    warnings: List[str] = []
    changed = False
    cur = doc.get("schema_version")
    if not isinstance(cur, str):
        return doc, MigrationReport(changed=False, steps=[], warnings=[])
    for _ in range(32):
        fn = MIGRATIONS.get(cur)
        if fn is None:
            break
        before = cur
        doc, w = fn(doc)
        warnings.extend(w)
        cur = doc.get("schema_version")
        steps.append(f"{label}{before} -> {cur}")
        changed = True
        if not isinstance(cur, str) or cur == before:
            warnings.append(f"Migration did not advance schema_version for {label!r} (stuck at {before})")
            break
    if changed:
        log.info("Applied migrations for %s: %s", label or "document", ", ".join(steps))
    return doc, MigrationReport(changed=changed, steps=steps, warnings=warnings)


def migrate_save_payload(doc: MutableMapping) -> Tuple[MutableMapping, MigrationReport]:
    return apply_migrations_to_document(doc, label="save:")
