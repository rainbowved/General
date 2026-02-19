from __future__ import annotations

import json
from typing import Any


def canonical_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json_bytes(obj: Any) -> bytes:
    return canonical_json_dumps(obj).encode("utf-8")
