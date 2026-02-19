from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from wt_client.core.content_pack import ContentPack


log = logging.getLogger("wt_client.validate_pack")


@dataclass
class HealthReport:
    pack_path: str
    mode: str
    root_hint: str
    ok: bool
    errors: List[str]
    warnings: List[str]


def validate_required_paths(pack: ContentPack, errors: List[str], warnings: List[str]) -> None:
    files = pack.list_files()
    has_prefix = lambda pre: any(f.startswith(pre) for f in files)

    if not pack.layout.specs_dir or not has_prefix("specs/"):
        errors.append("Missing required folder: specs/")

    if not pack.layout.demo_dir or not has_prefix("demo/"):
        errors.append("Missing required folder: demo/")

    if not pack.layout.db_bundle_dir:
        errors.append("Missing required folder: db_bundle* (expected a directory starting with 'db_bundle')")
    else:
        dbpre = pack.layout.db_bundle_dir.rstrip("/") + "/"
        if not has_prefix(dbpre):
            errors.append(f"db_bundle dir resolved as '{pack.layout.db_bundle_dir}/' but no files found under it")

        # Expect at least one sqlite in db_bundle.
        if not any(f.startswith(dbpre) and f.lower().endswith((".sqlite", ".db")) for f in files):
            errors.append(f"No sqlite files found under {dbpre} (expected *.sqlite)")

    if not pack.layout.concept:
        errors.append("Missing concept artifact: concept* (file at root) or concept/ folder")


def validate_specs_json_parse(pack: ContentPack, errors: List[str], warnings: List[str]) -> None:
    files = [f for f in pack.list_files() if f.startswith("specs/") and f.lower().endswith(".json")]
    if not files:
        errors.append("No JSON files found under specs/")
        return

    for f in files:
        try:
            pack.load_json(f)
        except Exception as e:
            errors.append(f"specs JSON parse failed: {f}: {e}")


def validate_turnpack_schema_load(pack: ContentPack, errors: List[str], warnings: List[str]) -> None:
    rel = "specs/turnpack_schema.json"
    try:
        obj = pack.load_json(rel)
        if not isinstance(obj, dict):
            warnings.append(f"turnpack_schema.json is not an object (dict) — got {type(obj).__name__}")
    except FileNotFoundError:
        errors.append(f"Missing required spec file: {rel}")
    except Exception as e:
        errors.append(f"Failed to load {rel}: {e}")


def validate_rng_streams_load(pack: ContentPack, errors: List[str], warnings: List[str]) -> None:
    rel = "specs/rng_streams.json"
    try:
        obj = pack.load_json(rel)
        if not isinstance(obj, (dict, list)):
            warnings.append(f"rng_streams.json unexpected top-level type: {type(obj).__name__}")
    except FileNotFoundError:
        errors.append(f"Missing required spec file: {rel}")
    except Exception as e:
        errors.append(f"Failed to load {rel}: {e}")


def validate_items_db_schema(pack: ContentPack, errors: List[str], warnings: List[str]) -> None:
    # Read-only schema reconnaissance: ensure item_id -> name mapping is possible.
    # This must never crash validation.
    try:
        from wt_client.core.item_catalog import ItemCatalog, ItemCatalogError
    except Exception:
        return

    try:
        cat = ItemCatalog(pack)
    except ItemCatalogError as e:
        warnings.append(f"ItemCatalog unavailable: {e}")
        return
    except Exception as e:
        warnings.append(f"ItemCatalog failed to initialize: {e}")
        return

    try:
        # Access internal schema guess via a benign lookup that will exercise SQL path.
        # If name column is missing, ItemCatalog will still work but will fall back to item_id.
        # We can inspect by asking the catalog for a guaranteed-missing ID.
        _ = cat.get("__nonexistent__")
        # Also, expose which sqlite is used for transparency.
        warnings.append(f"ItemCatalog sqlite: {cat.sqlite_relpath}")
    finally:
        try:
            cat.close()
        except Exception:
            pass



def validate_pack(pack: ContentPack, *, mode: str = "datapack") -> HealthReport:
    errors: List[str] = []
    warnings: List[str] = []

    try:
        if mode == "datapack":
            validate_required_paths(pack, errors, warnings)
            validate_specs_json_parse(pack, errors, warnings)
            validate_turnpack_schema_load(pack, errors, warnings)
            validate_rng_streams_load(pack, errors, warnings)
            validate_items_db_schema(pack, errors, warnings)
        elif mode == "dbbundle":
            dbpre = "" if pack.layout.db_bundle_dir in (None, ".") else pack.layout.db_bundle_dir.rstrip("/") + "/"
            files = pack.list_files()
            if not any(f.startswith(dbpre) and f.lower().endswith((".sqlite", ".db")) for f in files):
                errors.append("dbbundle mode: no sqlite files found")
        else:
            errors.append(f"Unknown health mode: {mode}")
    except Exception as e:
        errors.append(f"Validator crashed: {e}")

    ok = len(errors) == 0
    return HealthReport(
        pack_path=pack.source_path,
        mode=f"{pack.mode}:{mode}",
        root_hint=pack.layout.root,
        ok=ok,
        errors=errors,
        warnings=warnings,
    )


def format_health_report(rep: HealthReport) -> str:
    status = "OK" if rep.ok else "FAIL"
    lines: List[str] = []
    lines.append(f"[WT PACK HEALTH] {status}")
    lines.append(f"pack: {rep.pack_path}")
    lines.append(f"mode: {rep.mode}")
    lines.append(f"root: {rep.root_hint}")

    if rep.errors:
        lines.append("errors:")
        for e in rep.errors:
            lines.append(f"  - {e}")
    else:
        lines.append("errors: (none)")

    if rep.warnings:
        lines.append("warnings:")
        for w in rep.warnings:
            lines.append(f"  - {w}")
    else:
        lines.append("warnings: (none)")

    return "\n".join(lines) + "\n"
