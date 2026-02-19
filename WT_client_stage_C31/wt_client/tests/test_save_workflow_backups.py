from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import pytest

from wt_client.core.action_dispatcher import DispatchResult
from wt_client.core.master_changelog import apply_master_changelog
from wt_client.core.recent_actions import get_cursor
from wt_client.core.save_store import SaveStore
from wt_client.core.save_workflow import dispatch_and_autosave


def _mk_core_doc(schema: str, save_id: str, pack_version: str, updated_ts: str) -> Dict[str, Any]:
    return {
        "schema_version": schema,
        "save_id": save_id,
        "created_ts": "t0",
        "updated_ts": updated_ts,
        "pack_version": pack_version,
    }


def make_min_state(updated_ts: str = "t1") -> Dict[str, Any]:
    save_id = "SAVE_TEST"
    pack_version = "PACK_TEST"

    player = _mk_core_doc("0.6.6-player", save_id, pack_version, updated_ts)
    world = _mk_core_doc("0.6.6-world", save_id, pack_version, updated_ts)
    progress = _mk_core_doc("0.6.6-progress", save_id, pack_version, updated_ts)
    progress["cursor"] = {"seen_event_ids": [], "seen_hash": ""}
    progress["recent_actions"] = []
    inventory = _mk_core_doc("0.6.6-inventory", save_id, pack_version, updated_ts)
    session = {
        "schema_version": "0.6.6-session",
        "save_id": save_id,
        "session_id": "SES_TEST",
        "created_ts": "t0",
        "cursor": {"seen_event_ids": [], "seen_hash": ""},
        "rng_state": {},
    }

    return {
        "meta": {
            "save_id": save_id,
            "pack_version": pack_version,
            "layout": {
                "rel_player": "player.json",
                "rel_world": "world.json",
                "rel_progress": "progress.json",
                "rel_inventory": "inventory.json",
                "rel_session": "session.json",
            },
        },
        "player": player,
        "world": world,
        "progress": progress,
        "inventory": inventory,
        "session": session,
        "extras": {},
    }


@dataclass
class FakeDispatcher:
    result: DispatchResult

    def dispatch(
        self,
        action_request: Mapping[str, Any],
        state: Mapping[str, Any],
        cursor: Optional[Dict[str, Any]],
    ) -> DispatchResult:
        return self.result


def test_autosave_after_dispatch_writes_save(tmp_path: Path) -> None:
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    state = make_min_state("t1")
    store.save_save(save_dir, state, create_backup=False)

    new_state = make_min_state("t2")
    res = DispatchResult(
        ok=True,
        new_state=new_state,
        new_cursor=get_cursor(new_state) or {"seen_event_ids": [], "seen_hash": ""},
        events=[{"event_id": "E1", "type": "noop"}],
        ui_log=[],
        errors=[],
        warnings=[],
        applied=1,
    )
    dispatcher = FakeDispatcher(res)

    _, ar = dispatch_and_autosave(
        dispatcher,
        store=store,
        save_dir=save_dir,
        action_request={"type": "node_action", "action_id": "PROCEED"},
        state=state,
        cursor=get_cursor(state) or {"seen_event_ids": [], "seen_hash": ""},
    )

    assert ar.saved is True
    assert (save_dir / "progress.json").exists()
    txt = (save_dir / "progress.json").read_text(encoding="utf-8")
    assert "t2" in txt
    assert ar.backup_path is not None
    assert ar.backup_path.exists()


def test_autosave_not_called_on_dispatch_error(tmp_path: Path) -> None:
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    state = make_min_state("t1")
    store.save_save(save_dir, state, create_backup=False)

    res = DispatchResult(
        ok=False,
        new_state=state,
        new_cursor=get_cursor(state) or {"seen_event_ids": [], "seen_hash": ""},
        events=[],
        ui_log=[],
        errors=["boom"],
        warnings=[],
        applied=0,
    )
    dispatcher = FakeDispatcher(res)

    _, ar = dispatch_and_autosave(
        dispatcher,
        store=store,
        save_dir=save_dir,
        action_request={"type": "node_action", "action_id": "PROCEED"},
        state=state,
        cursor=get_cursor(state) or {"seen_event_ids": [], "seen_hash": ""},
    )

    assert ar.saved is False
    bdir = save_dir / store.BACKUPS_DIRNAME
    assert not bdir.exists() or not any(bdir.iterdir())


def test_backup_created_and_rolling_limit(tmp_path: Path) -> None:
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    # Write several versions; keep only last 3 backups.
    for i in range(6):
        st = make_min_state(f"t{i}")
        store.save_save(save_dir, st, create_backup=True, rolling_backups=3)

    bps = store.list_backups(save_dir)
    assert len(bps) == 3


def test_restore_backup_roundtrip_state_equal(tmp_path: Path) -> None:
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    st1 = make_min_state("t1")
    bp1 = store.save_save(save_dir, st1, create_backup=True, rolling_backups=10)
    assert bp1 is not None

    st2 = make_min_state("t2")
    store.save_save(save_dir, st2, create_backup=True, rolling_backups=10)

    # Restore the first snapshot.
    store.restore_backup(save_dir, bp1)
    loaded = store.load_save(save_dir)
    assert loaded["player"]["updated_ts"] == "t1"
    assert loaded["progress"]["updated_ts"] == "t1"


def test_failed_apply_does_not_corrupt_existing_save(tmp_path: Path) -> None:
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    st = make_min_state("t1")
    store.save_save(save_dir, st, create_backup=False)
    before = (save_dir / "player.json").read_bytes()

    broken = {"events": "not a list"}
    with pytest.raises(ValueError):
        # Should fail schema validation; autosave must not happen.
        apply_master_changelog(broken, state=st, cursor=get_cursor(st) or {"seen_event_ids": [], "seen_hash": ""})

    after = (save_dir / "player.json").read_bytes()
    assert before == after

    bdir = save_dir / store.BACKUPS_DIRNAME
    assert not bdir.exists() or not any(bdir.iterdir())
