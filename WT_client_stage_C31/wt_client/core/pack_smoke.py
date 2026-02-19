from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import zipfile
from typing import Iterable, List, Set, Tuple, Optional, Dict


log = logging.getLogger("wt_client.pack_smoke")

# Canonical expectations (as written in datapack spec).
CANON_REQUIRED = ("concept/", "db_bundle/", "specs/", "demo/")


@dataclass(frozen=True)
class SmokeReport:
    pack_path: str
    ok: bool
    root_prefix: str  # "" or "SomeRoot/"
    found: Tuple[str, ...]     # canonical keys that were satisfied
    missing: Tuple[str, ...]   # canonical keys that were NOT satisfied
    matched: Tuple[str, ...]   # what we actually matched (helpful when folders are versioned)
    entries_at_root: Tuple[str, ...]  # children at the effective root (after prefix)


def _normalize_zip_name(name: str) -> str:
    return name.replace("\\", "/")


def _top_level_dirs(names: Iterable[str]) -> Set[str]:
    out: Set[str] = set()
    for n in names:
        n = _normalize_zip_name(n)
        first = n.split("/", 1)[0]
        if first:
            out.add(first + "/")
    return out


def _choose_root_prefix(names: List[str]) -> str:
    tops = sorted(_top_level_dirs(names))
    # If the zip is wrapped in a single root folder (very common), detect it.
    if len(tops) == 1:
        return tops[0]  # e.g. "WT_data_release_candidate/"
    return ""


def _children_under_prefix(names: Iterable[str], prefix: str) -> Set[str]:
    """Immediate children under `prefix` (dirs end with '/'; files do not)."""
    pre = prefix
    info: Dict[str, bool] = {}  # child -> is_dir
    for n in names:
        n = _normalize_zip_name(n)
        if pre and not n.startswith(pre):
            continue
        rest = n[len(pre):] if pre else n
        if not rest:
            continue
        parts = rest.split("/", 1)
        first = parts[0]
        if not first:
            continue
        is_dir = False
        if len(parts) > 1:
            # Has deeper content => treat as directory child.
            is_dir = True
        if rest.endswith("/"):
            is_dir = True
        info[first] = info.get(first, False) or is_dir

    out: Set[str] = set()
    for child, is_dir in info.items():
        out.add(child + ("/" if is_dir else ""))
    return out


def _resolve_requirements(children: Set[str]) -> Tuple[List[str], List[str], List[str]]:
    found: List[str] = []
    missing: List[str] = []
    matched: List[str] = []

    # concept: allow either `concept/` folder OR any `concept*` file/folder shipped at root
    concept_ok = ("concept/" in children) or any(c.startswith("concept") for c in children)
    if concept_ok:
        found.append("concept/")
        for c in sorted(children):
            if c.startswith("concept"):
                matched.append(c)
                break
    else:
        missing.append("concept/")

    # db_bundle: allow exact `db_bundle/` OR versioned `db_bundle_*` dir
    db_ok = ("db_bundle/" in children) or any(c.startswith("db_bundle") for c in children)
    if db_ok:
        found.append("db_bundle/")
        for c in sorted(children):
            if c.startswith("db_bundle"):
                matched.append(c)
                break
    else:
        missing.append("db_bundle/")

    # specs: canonical only (dir)
    if "specs/" in children:
        found.append("specs/")
        matched.append("specs/")
    else:
        missing.append("specs/")

    # demo: canonical only (dir)
    if "demo/" in children:
        found.append("demo/")
        matched.append("demo/")
    else:
        missing.append("demo/")

    return found, missing, matched


def smoke_check_pack(pack_path: str) -> SmokeReport:
    p = Path(pack_path).expanduser()
    if not p.exists():
        msg = f"Pack not found: {p}"
        log.error(msg)
        return SmokeReport(
            pack_path=str(p),
            ok=False,
            root_prefix="",
            found=(),
            missing=tuple(CANON_REQUIRED),
            matched=(),
            entries_at_root=(),
        )

    with zipfile.ZipFile(str(p), "r") as zf:
        names = [_normalize_zip_name(n) for n in zf.namelist()]
        prefix = _choose_root_prefix(names)
        children = _children_under_prefix(names, prefix)
        children_sorted = tuple(sorted(children))

        found, missing, matched = _resolve_requirements(children)
        ok = len(missing) == 0

        log.info("Smoke check: ok=%s prefix=%s found=%s missing=%s", ok, prefix, found, missing)

        return SmokeReport(
            pack_path=str(p),
            ok=ok,
            root_prefix=prefix,
            found=tuple(found),
            missing=tuple(missing),
            matched=tuple(matched),
            entries_at_root=children_sorted,
        )


def format_report(rep: SmokeReport) -> str:
    status = "OK" if rep.ok else "FAIL"
    lines: List[str] = []
    lines.append(f"[WT PACK SMOKE] {status}")
    lines.append(f"pack: {rep.pack_path}")
    lines.append(f"root_prefix: {rep.root_prefix or '(none)'}")
    lines.append(f"required(canon): {', '.join(CANON_REQUIRED)}")
    lines.append(f"found(canon):    {', '.join(rep.found) if rep.found else '(none)'}")
    lines.append(f"missing(canon):  {', '.join(rep.missing) if rep.missing else '(none)'}")
    if rep.matched:
        lines.append(f"matched(actual): {', '.join(rep.matched)}")
    lines.append("entries@root:")
    for e in rep.entries_at_root:
        lines.append(f"  - {e}")
    return "\n".join(lines) + "\n"
