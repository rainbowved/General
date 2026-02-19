from __future__ import annotations

from pathlib import Path

import pytest

from wt_client.core.save_store import SaveIOError, SaveStore
from wt_client.tests.test_save_workflow_backups import make_min_state


def test_save_mid_swap_failure_keeps_old_save_intact(tmp_path: Path, monkeypatch) -> None:
    """Simulate a failure during directory swap (tmp -> dst).

    Expectation:
    - old save remains readable and unchanged
    - new save does not partially appear
    - temp dirs do not accumulate for the current run
    """
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    st1 = make_min_state("t1")
    store.save_save(save_dir, st1, create_backup=False)

    before = (save_dir / "player.json").read_text(encoding="utf-8")

    st2 = make_min_state("t2")

    # Patch os.replace used by SaveStore to fail only on tmp -> dst, but allow rollback.
    import wt_client.core.save_store as ss

    real_replace = ss.os.replace

    def flaky_replace(src: str, dst: str):
        # Fail only when moving the temp dir into the final save dir.
        if ".save_tmp" in src and dst.endswith(str(save_dir)):
            raise OSError("injected failure during tmp->dst")
        return real_replace(src, dst)

    monkeypatch.setattr(ss.os, "replace", flaky_replace)

    with pytest.raises(SaveIOError):
        store.save_save(save_dir, st2, create_backup=False)

    # Old save is still present and unchanged.
    after = (save_dir / "player.json").read_text(encoding="utf-8")
    assert after == before
    loaded = store.load_save(save_dir)
    assert loaded["player"]["updated_ts"] == "t1"

    # No current-run temp dirs should remain.
    leftovers = [
        p
        for p in tmp_path.iterdir()
        if p.is_dir() and (p.name.startswith(store.TMP_DIR_BASENAME) or ".swapbak_" in p.name)
    ]
    assert leftovers == []


def test_successful_save_leaves_no_swap_artifacts(tmp_path: Path) -> None:
    store = SaveStore()
    save_dir = tmp_path / "SAVE"

    st1 = make_min_state("t1")
    store.save_save(save_dir, st1, create_backup=False)

    st2 = make_min_state("t2")
    store.save_save(save_dir, st2, create_backup=False)

    loaded = store.load_save(save_dir)
    assert loaded["player"]["updated_ts"] == "t2"

    leftovers = [
        p
        for p in tmp_path.iterdir()
        if p.is_dir() and (p.name.startswith(store.TMP_DIR_BASENAME) or ".swapbak_" in p.name)
    ]
    assert leftovers == []
