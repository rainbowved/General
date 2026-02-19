from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Protocol, Tuple

from wt_client.core.action_dispatcher import DispatchResult
from wt_client.core.master_changelog import MasterChangelogSummary, apply_master_changelog
from wt_client.core.recent_actions import set_cursor
from wt_client.core.save_store import SaveIOError, SaveStore


log = logging.getLogger("wt_client.save_workflow")


class DispatcherLike(Protocol):
    def dispatch(
        self,
        action_request: Mapping[str, Any],
        state: Mapping[str, Any],
        cursor: Optional[Dict[str, Any]],
    ) -> DispatchResult: ...


@dataclass
class AutosaveResult:
    saved: bool
    backup_path: Optional[Path]
    message: str


def dispatch_and_autosave(
    dispatcher: DispatcherLike,
    *,
    store: SaveStore,
    save_dir: str | Path,
    action_request: Mapping[str, Any],
    state: Dict[str, Any],
    cursor: Optional[Dict[str, Any]],
) -> Tuple[DispatchResult, AutosaveResult]:
    """Dispatch an action and autosave only if something was applied."""
    res = dispatcher.dispatch(action_request, state, cursor)
    if not res.ok:
        return res, AutosaveResult(saved=False, backup_path=None, message="dispatch failed")

    if res.applied <= 0:
        return res, AutosaveResult(saved=False, backup_path=None, message="no changes")

    try:
        # Persist cursor for idempotency.
        try:
            set_cursor(res.new_state, res.new_cursor)
        except Exception:
            pass
        bp = store.save_save(save_dir, res.new_state, create_backup=True)
        return res, AutosaveResult(saved=True, backup_path=bp, message="saved")
    except SaveIOError as e:
        # Keep UX clean; callers decide how to present.
        log.exception("autosave failed")
        return res, AutosaveResult(saved=False, backup_path=None, message=str(e))


def apply_master_changelog_and_autosave(
    master_doc: Any,
    *,
    store: SaveStore,
    save_dir: str | Path,
    state: Dict[str, Any],
    cursor: Dict[str, Any],
    lenient: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any], MasterChangelogSummary, AutosaveResult]:
    """Apply master CHANGELOG and autosave only if events were applied."""
    st, cur, summary = apply_master_changelog(master_doc, state=state, cursor=cursor, lenient=lenient)

    # Persist cursor for idempotency.
    try:
        set_cursor(st, cur)
    except Exception:
        pass

    if summary.applied <= 0:
        return st, cur, summary, AutosaveResult(saved=False, backup_path=None, message="no changes")

    try:
        bp = store.save_save(save_dir, st, create_backup=True)
        return st, cur, summary, AutosaveResult(saved=True, backup_path=bp, message="saved")
    except SaveIOError as e:
        log.exception("autosave failed")
        return st, cur, summary, AutosaveResult(saved=False, backup_path=None, message=str(e))
