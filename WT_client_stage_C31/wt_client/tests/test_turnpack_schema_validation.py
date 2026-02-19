import os
import json
import zipfile
from pathlib import Path

import pytest

from wt_client.core.save_store import SaveStore
from wt_client.core.changelog_engine import ChangelogEngine
from wt_client.core.turnpack_builder import TurnpackBuilder, TurnpackMeta
from wt_client.core.schema_validate import validate_turnpack


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


def _find_prefix(z: zipfile.ZipFile, tail: str) -> str:
    for n in z.namelist():
        if n.endswith(tail):
            return n[: -len(tail)]
    raise AssertionError(f"Could not locate {tail} inside the pack")


def _extract_demo_to(tmp_path: Path) -> Path:
    out = tmp_path / "demo_save"
    out.mkdir(parents=True, exist_ok=True)
    assert PACK_PATH is not None
    with zipfile.ZipFile(str(PACK_PATH), "r") as z:
        prefix = _find_prefix(z, "demo/save/player.json")
        wanted = [
            "demo/save/player.json",
            "demo/save/world.json",
            "demo/save/progress.json",
            "demo/save/inventory.json",
            "demo/session/session.json",
        ]
        for rel in wanted:
            src = prefix + rel
            if src not in z.namelist():
                if rel.endswith("session.json"):
                    continue
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


def _load_schema_and_events() -> tuple[dict, list[dict], str, str, str]:
    assert PACK_PATH is not None
    with zipfile.ZipFile(str(PACK_PATH), "r") as z:
        prefix = _find_prefix(z, "specs/turnpack_schema.json")
        schema = json.loads(z.read(prefix + "specs/turnpack_schema.json").decode("utf-8"))

        ch_prefix = _find_prefix(z, "demo/changelog/changelog.json")
        ch = json.loads(z.read(ch_prefix + "demo/changelog/changelog.json").decode("utf-8"))
        events = ch.get("events") if isinstance(ch, dict) else []
        assert isinstance(events, list)

        # content and db bundle versions are not hard-coded; infer from pack.
        content_version = prefix.strip("/").split("/")[0] or "WT"
        db_bundle_version = None
        # Look for a folder starting with db_bundle in root.
        for n in z.namelist():
            if n.startswith(content_version + "/db_bundle"):
                # take first folder name
                rest = n[len(content_version) + 1 :]
                db_bundle_version = rest.split("/", 1)[0]
                break
        db_bundle_version = db_bundle_version or "db_bundle"
        schema_version = schema.get("$id") or "turnpack_schema"
        return schema, events, schema_version, content_version, db_bundle_version


@pytest.mark.rc_pack
def test_turnpack_validates_on_demo(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    store = SaveStore()
    state = store.load_save(demo_root)

    schema_json, events, schema_version, content_version, db_bundle_version = _load_schema_and_events()
    eng = ChangelogEngine()
    state2, cursor2, applied = eng.apply(events, state, cursor=None)
    assert applied == len(events)

    meta = TurnpackMeta(
        schema_version=schema_version,
        content_version=content_version,
        db_bundle_version=db_bundle_version,
        cursor=len(cursor2.get("seen_event_ids") or []),
    )
    tp = TurnpackBuilder().build(state2, recent_actions=events, meta=meta)
    ok, errors = validate_turnpack(tp, schema_json)
    assert ok, f"Expected schema OK, got errors: {errors}"


@pytest.mark.rc_pack
def test_turnpack_validator_catches_corruption(tmp_path: Path):
    assert PACK_PATH is not None
    demo_root = _extract_demo_to(tmp_path)
    store = SaveStore()
    state = store.load_save(demo_root)
    schema_json, events, schema_version, content_version, db_bundle_version = _load_schema_and_events()
    state2, cursor2, _applied = ChangelogEngine().apply(events, state, cursor=None)

    meta = TurnpackMeta(
        schema_version=schema_version,
        content_version=content_version,
        db_bundle_version=db_bundle_version,
        cursor=len(cursor2.get("seen_event_ids") or []),
    )
    tp = TurnpackBuilder().build(state2, recent_actions=events, meta=meta)

    # Corrupt a required field type.
    tp["cursor"] = "NOPE"
    ok, errors = validate_turnpack(tp, schema_json)
    assert not ok
    assert any(er.path == "cursor" for er in errors)
