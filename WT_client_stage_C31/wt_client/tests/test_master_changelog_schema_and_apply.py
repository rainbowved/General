from __future__ import annotations

from wt_client.core.master_changelog import apply_master_changelog, validate_master_changelog


def _base_state() -> dict:
    return {
        "world": {"world": {"location": {"region": "CITY", "location_id": "HUB", "sub_id": "SQUARE"}}},
        "session": {},
        "inventory": {"items": []},
        "meta": {},
    }


def test_master_changelog_schema_accepts_list_or_object():
    ev = {"event_id": "e1", "type": "MODE_SET", "payload": {"mode": "CAMP"}}

    ok1, errs1 = validate_master_changelog([ev], lenient=False)
    assert ok1, [f"{e.path}: {e.message}" for e in errs1]

    ok2, errs2 = validate_master_changelog({"events": [ev], "source": "master"}, lenient=False)
    assert ok2, [f"{e.path}: {e.message}" for e in errs2]


def test_apply_master_changelog_idempotent():
    doc = [{"event_id": "e1", "type": "MODE_SET", "payload": {"mode": "CAMP"}}]
    st0 = _base_state()

    st1, cur1, s1 = apply_master_changelog(doc, state=st0, cursor=None, lenient=False)
    assert s1.applied == 1
    assert st1["session"]["active_mode"] == "CAMP"

    st2, cur2, s2 = apply_master_changelog(doc, state=st1, cursor=cur1, lenient=False)
    assert s2.applied == 0
    assert s2.skipped_duplicates >= 1
    assert st1 == st2
    assert cur1 == cur2


def test_master_changelog_rejects_unknown_event_strict():
    doc = {"events": [{"event_id": "x", "type": "NOPE", "payload": {}}]}
    ok, errs = validate_master_changelog(doc, lenient=False)
    assert not ok
    assert errs


def test_master_changelog_lenient_skips_unknown_with_warning():
    doc = {
        "events": [
            {"event_id": "e1", "type": "MODE_SET", "payload": {"mode": "CAMP"}},
            {"event_id": "e2", "type": "NOPE", "payload": {"x": 1}},
        ]
    }
    st0 = _base_state()
    st1, cur1, s1 = apply_master_changelog(doc, state=st0, cursor=None, lenient=True)
    assert st1["session"]["active_mode"] == "CAMP"
    assert s1.applied == 1
    assert s1.unknown_ignored == 1
    assert s1.warnings
    assert any("Ignored unknown" in w for w in s1.warnings)
