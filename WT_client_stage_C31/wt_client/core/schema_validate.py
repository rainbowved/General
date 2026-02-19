from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable, List, Tuple


log = logging.getLogger("wt_client.schema_validate")


@dataclass(frozen=True)
class SchemaError:
    path: str
    message: str


def _fmt_path(parts: Iterable[Any]) -> str:
    out: List[str] = []
    for p in parts:
        if isinstance(p, int):
            out.append(f"[{p}]")
        else:
            if not out:
                out.append(str(p))
            else:
                out.append("." + str(p))
    return "".join(out) or "$"


def validate_turnpack(turnpack: dict, schema_json: dict) -> Tuple[bool, List[SchemaError]]:
    """Validate TURNPACK against a draft-07 JSON schema.

    Returns (ok, errors). Errors are human-readable and include a best-effort path.
    """
    try:
        from jsonschema import Draft7Validator
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "jsonschema dependency is required for schema validation. Install 'jsonschema'."
        ) from e

    v = Draft7Validator(schema_json)
    errors = sorted(v.iter_errors(turnpack), key=lambda er: (list(er.path), er.message))
    out: List[SchemaError] = []
    for er in errors:
        out.append(SchemaError(path=_fmt_path(er.path), message=er.message))

    ok = len(out) == 0
    if not ok:
        log.warning("TURNPACK schema validation failed: %d error(s)", len(out))
    return ok, out


def validate_json_schema(doc: Any, schema_json: dict) -> Tuple[bool, List[SchemaError]]:
    """Validate any JSON-ish document against a draft-07 JSON schema.

    Returns (ok, errors). Errors are human-readable and include a best-effort path.
    """
    try:
        from jsonschema import Draft7Validator
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "jsonschema dependency is required for schema validation. Install 'jsonschema'."
        ) from e

    v = Draft7Validator(schema_json)
    errors = sorted(v.iter_errors(doc), key=lambda er: (list(er.path), er.message))
    out: List[SchemaError] = []
    for er in errors:
        out.append(SchemaError(path=_fmt_path(er.path), message=er.message))
    return len(out) == 0, out
