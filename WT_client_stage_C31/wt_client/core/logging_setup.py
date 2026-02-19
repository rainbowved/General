from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(logs_dir: str, *, log_name: str = "wt_client.log", level: int = logging.INFO) -> Path:
    """Console + file logging. Creates logs_dir if needed.

    UX invariant for WT client: do not print Python tracebacks in UI/CLI.
    Tracebacks must go to a logfile.

    Therefore the console handler is WARNING+ by default, while the file handler
    keeps the configured level.
    """
    logs_path = Path(logs_dir).expanduser().resolve()
    logs_path.mkdir(parents=True, exist_ok=True)
    logfile = logs_path / log_name

    logger = logging.getLogger()
    logger.setLevel(level)

    # Avoid duplicate handlers in re-entrant calls/tests.
    for h in list(logger.handlers):
        logger.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    sh = logging.StreamHandler(sys.stdout)
    # Keep console relatively quiet; detailed logs go to file.
    sh.setLevel(logging.WARNING)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    fh = logging.FileHandler(str(logfile), encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logging.getLogger("wt_client").info("Logging initialized. logfile=%s", logfile)
    return logfile
