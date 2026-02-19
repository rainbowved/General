from __future__ import annotations

import io
import json
import logging
import os
import sqlite3
import tempfile
import zipfile

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple


log = logging.getLogger("wt_client.content_pack")


def _norm_rel(p: str) -> str:
    # Normalize a relative path for pack lookups.
    # - zip members never start with "./" in practice
    # - callers sometimes join paths with a leading "./"
    s = p.replace("\\", "/").lstrip("/")
    while s.startswith("./"):
        s = s[2:]
    return s


def _is_junk_top(name: str) -> bool:
    # Common ZIP junk / platform metadata
    n = _norm_rel(name)
    return n.startswith("__MACOSX/") or n.startswith(".DS_Store") or n.startswith("._")


def _top_level_dirs(names: Iterable[str]) -> List[str]:
    out = set()
    for n in names:
        if _is_junk_top(n):
            continue
        n = _norm_rel(n)
        if not n or "/" not in n:
            continue
        out.add(n.split("/", 1)[0] + "/")
    return sorted(out)


def _children_under_prefix(names: Iterable[str], prefix: str) -> set[str]:
    pre = _norm_rel(prefix)
    if pre and not pre.endswith("/"):
        pre += "/"
    info: dict[str, bool] = {}
    for n in names:
        if _is_junk_top(n):
            continue
        n = _norm_rel(n)
        if pre and not n.startswith(pre):
            continue
        rest = n[len(pre) :] if pre else n
        if not rest:
            continue
        parts = rest.split("/", 1)
        first = parts[0]
        if not first:
            continue
        is_dir = False
        if len(parts) > 1:
            is_dir = True
        if rest.endswith("/"):
            is_dir = True
        info[first] = info.get(first, False) or is_dir
    out: set[str] = set()
    for child, is_dir in info.items():
        out.add(child + ("/" if is_dir else ""))
    return out


def _score_root_children(children: set[str]) -> int:
    score = 0
    # Strongly prefer full datapack roots (specs + db_bundle + demo).
    if "specs/" in children and any(c.startswith("db_bundle") and c.endswith("/") for c in children):
        score += 6
    bare_markers = {
        "rpg_items.sqlite",
        "rpg_items_write.sqlite",
        "rpg_bestiary.sqlite",
        "schema.sql",
    }
    if children & bare_markers:
        score += 3
    if "specs/" in children:
        score += 1
    if "demo/" in children:
        score += 1
    if any(c.startswith("db_bundle") and c.endswith("/") for c in children):
        score += 1
    # concept: can be folder or file
    if ("concept/" in children) or any(c.lower().startswith("concept") for c in children):
        score += 1
    return score


def _choose_zip_root_prefix(names: Sequence[str]) -> str:
    # Candidates: no prefix, or any top-level directory.
    candidates = [""] + _top_level_dirs(names)
    best = ""
    best_score = -1
    for pre in candidates:
        children = _children_under_prefix(names, pre)
        s = _score_root_children(children)
        if s > best_score:
            best_score = s
            best = pre
    return best


def _choose_dir_root_path(base: Path) -> Path:
    base = base.resolve()
    candidates = [base]
    try:
        for child in base.iterdir():
            if child.is_dir():
                candidates.append(child)
    except OSError:
        return base

    best = base
    best_score = -1
    for cand in candidates:
        try:
            children = set()
            for c in cand.iterdir():
                if c.is_dir():
                    children.add(c.name + "/")
                else:
                    children.add(c.name)
            s = _score_root_children(children)
        except OSError:
            continue
        if s > best_score:
            best_score = s
            best = cand
    return best


@dataclass(frozen=True)
class PackLayout:
    root: str  # for zip: prefix; for dir: '.'
    concept: Tuple[str, ...]
    specs_dir: Optional[str]
    demo_dir: Optional[str]
    db_bundle_dir: Optional[str]


class ContentPack:
    """Abstraction over a datapack delivered as ZIP or a directory.

    All paths exposed by this class are *relative* to the detected pack root.
    """

    def __init__(self) -> None:
        self._layout: Optional[PackLayout] = None

    @property
    def mode(self) -> str:
        raise NotImplementedError

    @property
    def source_path(self) -> str:
        raise NotImplementedError

    @property
    def layout(self) -> PackLayout:
        assert self._layout is not None
        return self._layout

    def close(self) -> None:
        return None

    def __enter__(self) -> "ContentPack":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # --- file API ---
    def list_files(self) -> List[str]:
        raise NotImplementedError

    def open_binary(self, relpath: str) -> bytes:
        raise NotImplementedError

    def open_text(self, relpath: str, encoding: str = "utf-8") -> str:
        data = self.open_binary(relpath)
        return data.decode(encoding)

    def load_json(self, relpath: str):
        txt = self.open_text(relpath)
        return json.loads(txt)

    def open_sqlite(self, relpath: str) -> sqlite3.Connection:
        raise NotImplementedError

    # --- helpers ---
    def _compute_layout_from_files(self, files: Sequence[str], root_hint: str) -> PackLayout:
        # files are already relative-to-root.
        root_children = set()
        for f in files:
            parts = _norm_rel(f).split("/", 1)
            if len(parts) == 1:
                root_children.add(parts[0])
            else:
                root_children.add(parts[0] + "/")

        concept_candidates = sorted(
            [c for c in root_children if c.lower().startswith("concept")]
        )
        concept: List[str] = []
        if "concept/" in root_children:
            # pick all files under concept/
            concept = sorted([f for f in files if f.startswith("concept/")])
        else:
            # treat any root-level file starting with concept as the concept artifact
            for c in concept_candidates:
                if not c.endswith("/"):
                    concept.append(c)

        specs_dir = "specs" if "specs/" in root_children else None
        demo_dir = "demo" if "demo/" in root_children else None

        db_dirs = sorted([c[:-1] for c in root_children if c.endswith("/") and c.startswith("db_bundle")])
        db_bundle_dir = None
        if "db_bundle" in db_dirs:
            db_bundle_dir = "db_bundle"
        elif len(db_dirs) == 1:
            db_bundle_dir = db_dirs[0]
        elif len(db_dirs) > 1:
            # Prefer the shortest (often base) deterministically.
            db_bundle_dir = sorted(db_dirs, key=lambda s: (len(s), s))[0]

        # If the *pack itself* is a bare db_bundle (no enclosing db_bundle/ folder),
        # treat the pack root as db_bundle.
        if db_bundle_dir is None:
            bare_markers = {
                "rpg_items.sqlite",
                "rpg_items_write.sqlite",
                "rpg_bestiary.sqlite",
                "schema.sql",
            }
            if (root_children & bare_markers) or ("json/" in root_children) or ("content/" in root_children):
                db_bundle_dir = "."

        return PackLayout(root=root_hint, concept=tuple(concept), specs_dir=specs_dir, demo_dir=demo_dir, db_bundle_dir=db_bundle_dir)


class _ZipContentPack(ContentPack):
    def __init__(self, zip_path: Path, root_prefix: str) -> None:
        super().__init__()
        self._zip_path = zip_path
        self._zip = zipfile.ZipFile(str(zip_path), "r")
        self._prefix = _norm_rel(root_prefix)
        if self._prefix and not self._prefix.endswith("/"):
            self._prefix += "/"
        self._tmp = tempfile.TemporaryDirectory(prefix="wt_pack_")
        self._extracted_sqlite: dict[str, Path] = {}
        self._files = self._build_file_list()
        self._layout = self._compute_layout_from_files(self._files, root_hint=(self._prefix or "(none)"))

    @property
    def mode(self) -> str:
        return "zip"

    @property
    def source_path(self) -> str:
        return str(self._zip_path)

    def close(self) -> None:
        try:
            self._zip.close()
        finally:
            self._tmp.cleanup()

    def _build_file_list(self) -> List[str]:
        out: List[str] = []
        for n in self._zip.namelist():
            if _is_junk_top(n):
                continue
            n = _norm_rel(n)
            if n.endswith("/"):
                continue
            if self._prefix and not n.startswith(self._prefix):
                continue
            rel = n[len(self._prefix) :] if self._prefix else n
            rel = _norm_rel(rel)
            if rel:
                out.append(rel)
        return sorted(out)

    def list_files(self) -> List[str]:
        return list(self._files)

    def open_binary(self, relpath: str) -> bytes:
        rel = _norm_rel(relpath)
        name = (self._prefix + rel) if self._prefix else rel
        try:
            with self._zip.open(name, "r") as fp:
                return fp.read()
        except KeyError as e:
            raise FileNotFoundError(f"Missing file in zip pack: {rel}") from e

    def open_sqlite(self, relpath: str) -> sqlite3.Connection:
        rel = _norm_rel(relpath)
        # Extract to temp once.
        if rel not in self._extracted_sqlite:
            data = self.open_binary(rel)
            out_path = Path(self._tmp.name) / Path(rel).name
            out_path.write_bytes(data)
            self._extracted_sqlite[rel] = out_path

        p = self._extracted_sqlite[rel]
        return _connect_sqlite_readonly(p)


class _DirContentPack(ContentPack):
    def __init__(self, root_dir: Path) -> None:
        super().__init__()
        self._root = root_dir
        self._files = self._build_file_list()
        self._layout = self._compute_layout_from_files(self._files, root_hint=str(self._root))

    @property
    def mode(self) -> str:
        return "dir"

    @property
    def source_path(self) -> str:
        return str(self._root)

    def list_files(self) -> List[str]:
        return list(self._files)

    def _build_file_list(self) -> List[str]:
        out: List[str] = []
        for p in self._root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(self._root).as_posix()
            out.append(rel)
        return sorted(out)

    def open_binary(self, relpath: str) -> bytes:
        rel = _norm_rel(relpath)
        p = self._root / rel
        if not p.exists() or not p.is_file():
            if rel.startswith("specs/"):
                alt = self._root / ("content/core/" + rel.split("/",1)[1])
                if alt.exists() and alt.is_file():
                    return alt.read_bytes()
            raise FileNotFoundError(f"Missing file in dir pack: {rel}")
        return p.read_bytes()

    def open_sqlite(self, relpath: str) -> sqlite3.Connection:
        rel = _norm_rel(relpath)
        p = (self._root / rel).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Missing sqlite in dir pack: {rel}")
        return _connect_sqlite_readonly(p)


def _connect_sqlite_readonly(path: Path) -> sqlite3.Connection:
    # Best-effort read-only, with safe fallback.
    try:
        conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        return conn
    except sqlite3.OperationalError:
        conn = sqlite3.connect(str(path))
        try:
            conn.execute("PRAGMA query_only = ON;")
        except sqlite3.DatabaseError:
            pass
        return conn


class ContentPackLoader:
    """Loads a datapack from ZIP or directory, detecting the effective pack root."""

    def load(self, path: str | os.PathLike[str]) -> ContentPack:
        p = Path(path).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"Pack not found: {p}")

        if p.is_file() and zipfile.is_zipfile(str(p)):
            with zipfile.ZipFile(str(p), "r") as zf:
                names = zf.namelist()
            root_prefix = _choose_zip_root_prefix(names)
            log.info("Loaded zip pack %s (root_prefix=%s)", p, root_prefix or "(none)")
            return _ZipContentPack(p, root_prefix)

        if p.is_dir():
            root = _choose_dir_root_path(p)
            log.info("Loaded dir pack %s (root_dir=%s)", p, root)
            return _DirContentPack(root)

        raise ValueError(f"Unsupported pack path (not a zip or dir): {p}")
