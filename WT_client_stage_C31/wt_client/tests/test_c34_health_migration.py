from __future__ import annotations

import json
from pathlib import Path

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.migrations import migrate_save_payload
from wt_client.core.validate_pack import validate_pack


def test_health_dbbundle_root_mode(tmp_path: Path) -> None:
    (tmp_path / "rpg_items.sqlite").write_bytes(b"sqlite")
    loader = ContentPackLoader()
    with loader.load(str(tmp_path)) as pack:
        rep = validate_pack(pack, mode="dbbundle")
    assert rep.ok


def test_migrate_save_roundtrip() -> None:
    old = {
        "schema_version": "0.6.3-save1",
        "cursor": {"seen_event_ids": ["a"], "seen_hash": "x"},
        "player": {"meters": {"fat_current": 120, "thirst": -3}},
    }
    new_doc, rep = migrate_save_payload(old)
    assert rep.changed
    assert new_doc["schema_version"] == "0.6.5-save1"
    assert new_doc["session"]["cursor"]["seen_hash"] == "x"
    assert new_doc["player"]["meters"]["fat_current"] == 100
    assert new_doc["player"]["meters"]["thirst"] == 0
    blob = json.dumps(new_doc, sort_keys=True)
    assert json.loads(blob)["schema_version"] == "0.6.5-save1"
