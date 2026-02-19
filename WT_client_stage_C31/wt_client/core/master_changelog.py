from __future__ import annotations

import copy
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from wt_client.core.changelog_engine import ChangelogEngine
from wt_client.core.schema_validate import SchemaError, validate_json_schema


log = logging.getLogger("wt_client.master_changelog")


@dataclass(frozen=True)
class ParsedMasterChangelog:
    events: List[Dict[str, Any]]
    meta: Dict[str, Any]


@dataclass(frozen=True)
class MasterChangelogSummary:
    events_total: int
    applied: int
    skipped_duplicates: int
    unknown_ignored: int
    warnings: List[str]


def parse_master_changelog(doc: Any) -> ParsedMasterChangelog:
    """Parse master CHANGELOG container.

    Supported containers:
      A) list[event]
      B) {"events": list[event], ...optional_meta}
    """
    if isinstance(doc, list):
        events = [e for e in doc if isinstance(e, dict)]
        return ParsedMasterChangelog(events=events, meta={})

    if isinstance(doc, dict):
        evs = doc.get("events")
        if isinstance(evs, list):
            events = [e for e in evs if isinstance(e, dict)]
            meta = {k: v for k, v in doc.items() if k != "events"}
            return ParsedMasterChangelog(events=events, meta=meta)

    raise ValueError("master changelog: expected list of events or object with 'events' list")


def _load_schema_text() -> str:
    # Package resource: wt_client/specs/master_changelog_schema.json
    try:
        import importlib.resources as ir

        return (
            ir.files("wt_client.specs")
            .joinpath("master_changelog_schema.json")
            .read_text(encoding="utf-8")
        )
    except Exception:
        # Fallback for direct source runs.
        from pathlib import Path

        here = Path(__file__).resolve()
        p = here.parents[1] / "specs" / "master_changelog_schema.json"
        return p.read_text(encoding="utf-8")


def load_master_changelog_schema(*, lenient: bool = False) -> Dict[str, Any]:
    schema = json.loads(_load_schema_text())
    if not lenient:
        return schema

    # Lenient mode: accept unknown event "type" values in schema, then filter them explicitly.
    relaxed = copy.deepcopy(schema)
    try:
        defs = relaxed.get("definitions")
        if isinstance(defs, dict):
            ev = defs.get("event")
            if isinstance(ev, dict):
                props = ev.get("properties")
                if isinstance(props, dict):
                    tprop = props.get("type")
                    if isinstance(tprop, dict):
                        tprop.pop("enum", None)
    except Exception:
        pass

    return relaxed


def validate_master_changelog(doc: Any, *, lenient: bool = False) -> Tuple[bool, List[SchemaError]]:
    schema = load_master_changelog_schema(lenient=lenient)
    return validate_json_schema(doc, schema)


def filter_unknown_events(
    events: Iterable[Dict[str, Any]],
    *,
    lenient: bool,
) -> Tuple[List[Dict[str, Any]], int, List[str]]:
    """Strict: return events unchanged (unknown should already be blocked by schema).
    Lenient: skip unknown types with warnings.
    """
    supported = ChangelogEngine.supported_event_types()
    out: List[Dict[str, Any]] = []
    unknown = 0
    warns: List[str] = []
    for idx, ev in enumerate(events):
        et = ev.get("type")
        if isinstance(et, str) and et in supported:
            out.append(ev)
            continue

        if lenient:
            unknown += 1
            eid = ev.get("event_id")
            if isinstance(eid, str) and eid:
                warns.append(f"Ignored unknown event type: {et} (event_id={eid})")
            else:
                warns.append(f"Ignored unknown event type: {et} (events[{idx}])")
            continue

        out.append(ev)

    return out, unknown, warns


def compute_skipped_duplicates(events: Iterable[Dict[str, Any]], cursor: Optional[Mapping[str, Any]]) -> int:
    seen_pre: set[str] = set()
    if isinstance(cursor, Mapping):
        xs = cursor.get("seen_event_ids")
        if isinstance(xs, list):
            for x in xs:
                if isinstance(x, str):
                    seen_pre.add(x)

    local = set(seen_pre)
    dups = 0
    for ev in events:
        eid = ev.get("event_id")
        if not isinstance(eid, str) or not eid:
            continue
        if eid in local:
            dups += 1
        else:
            local.add(eid)
    return dups


def apply_master_changelog(
    doc: Any,
    *,
    state: Dict[str, Any],
    cursor: Optional[Dict[str, Any]],
    lenient: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any], MasterChangelogSummary]:
    """Validate+parse+apply master changelog with a useful summary.

    Raises ValueError for validation errors.
    May raise ChangelogApplyError from ChangelogEngine on apply problems.
    """
    ok, errs = validate_master_changelog(doc, lenient=lenient)
    if not ok:
        lines = [f"{e.path}: {e.message}" for e in errs]
        raise ValueError("Schema validation failed:\n" + "\n".join(lines))

    parsed = parse_master_changelog(doc)
    events_total = len(parsed.events)
    filtered, unknown_ignored, warns = filter_unknown_events(parsed.events, lenient=lenient)

    skipped_duplicates = compute_skipped_duplicates(filtered, cursor)

    eng = ChangelogEngine()
    new_state, new_cursor, applied = eng.apply(filtered, state, cursor=cursor)

    summary = MasterChangelogSummary(
        events_total=events_total,
        applied=applied,
        skipped_duplicates=skipped_duplicates,
        unknown_ignored=unknown_ignored,
        warnings=warns,
    )
    return new_state, new_cursor, summary
