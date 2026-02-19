from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pytest


RC_ENV = "WT_TEST_PACK"


def rc_pack_path() -> Optional[Path]:
    val = os.environ.get(RC_ENV)
    if not val:
        return None
    return Path(val).expanduser()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "rc_pack: integration test that requires WT_TEST_PACK pointing to WT_data_release_candidate.zip",
    )


def pytest_sessionstart(session: pytest.Session) -> None:
    p = rc_pack_path()
    if p is not None and not p.exists():
        # If user explicitly asked for RC tests, fail early and clearly.
        pytest.exit(f"{RC_ENV} was set but pack not found: {p}", returncode=2)


def pytest_runtest_setup(item: pytest.Item) -> None:
    if "rc_pack" in item.keywords:
        if rc_pack_path() is None:
            pytest.skip(f"RC integration test not run (set {RC_ENV}=<path to WT_data_release_candidate.zip>)")


def pytest_terminal_summary(terminalreporter, exitstatus: int, config: pytest.Config) -> None:
    # Make it explicit whether RC integration tests were executed.
    p = rc_pack_path()
    if p is None:
        terminalreporter.write_line(f"\n[WT] RC integration tests: NOT RUN (set {RC_ENV}=... to enable)")
    else:
        terminalreporter.write_line(f"\n[WT] RC integration tests: enabled via {RC_ENV}={p}")
        terminalreporter.write_line("[WT] RC integration tests: scheduled to run (marked rc_pack)")
