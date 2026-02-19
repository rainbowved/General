import json
import zipfile
from pathlib import Path


from wt_client.core.support_bundle import create_support_bundle


def test_support_bundle_creates_zip_with_logs_and_meta(tmp_path: Path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / "wt_client.log").write_text("hello\n", encoding="utf-8")
    (logs_dir / "traceback.log").write_text("tb\n", encoding="utf-8")
    (logs_dir / "last_turnpack.json").write_text(json.dumps({"cursor": 1}), encoding="utf-8")

    save_dir = tmp_path / "save"
    save_dir.mkdir(parents=True, exist_ok=True)

    state = {
        "meta": {"pack_version": "RC_0.6.6"},
        "session": {"cursor": {"seen_event_ids": ["E1", "E2"], "seen_hash": "abc"}},
        "rng": {"schema": "rng_state.pcg32.v1", "master_seed": "seed123", "streams": {}},
    }

    res = create_support_bundle(
        logs_dir=logs_dir,
        save_dir=save_dir,
        pack_path="WT_data_release_candidate.zip",
        state=state,
    )

    assert res.path.exists()
    with zipfile.ZipFile(res.path, "r") as z:
        names = set(z.namelist())
        assert "meta/support_meta.json" in names
        assert "meta/save_slot.json" in names
        assert "logs/wt_client.log" in names
        assert "logs/traceback.log" in names
        assert "turnpack/last_turnpack.json" in names

        meta = json.loads(z.read("meta/support_meta.json").decode("utf-8"))
        assert meta["save_meta"]["cursor"]["seen_event_ids_count"] == 2
        assert meta["save_meta"]["seed"] == "seed123"
        assert meta["save_meta"]["pack_id"] == "RC_0.6.6"
