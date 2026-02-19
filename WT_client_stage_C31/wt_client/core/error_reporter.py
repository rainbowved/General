from __future__ import annotations

import datetime as _dt
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type


@dataclass(frozen=True)
class ErrorContext:
    """Lightweight context for error reporting.

    We keep it intentionally tiny: no gameplay logic, no extra mechanics.
    """

    where: str


class ErrorReporter:
    """Writes full tracebacks to a logfile, while keeping UI/CLI output clean."""

    def __init__(self, logs_dir: str | Path = ".wt_logs", *, filename: str = "traceback.log") -> None:
        self.logs_dir = Path(logs_dir).expanduser()
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.logfile = self.logs_dir / filename

    def write_traceback(
        self,
        exc_type: Type[BaseException],
        exc: BaseException,
        tb,
        *,
        context: Optional[ErrorContext] = None,
    ) -> None:
        ts = _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        where = f" | where={context.where}" if context else ""
        header = f"\n--- {ts}{where} ---\n"
        body = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            with self.logfile.open("a", encoding="utf-8") as f:
                f.write(header)
                f.write(body)
        except Exception:
            # Last resort: never crash while reporting an exception.
            pass

    def install_sys_excepthook(self) -> None:
        """Replace sys.excepthook to avoid printing tracebacks to stderr."""

        reporter = self

        def _hook(exc_type, exc, tb):
            # Respect KeyboardInterrupt: it is user intent.
            if exc_type is KeyboardInterrupt:
                return
            reporter.write_traceback(exc_type, exc, tb, context=ErrorContext(where="sys.excepthook"))
            # Minimal message; no traceback.
            try:
                sys.stderr.write(
                    f"FATAL: {exc_type.__name__}: {exc}\nSee log: {reporter.logfile}\n"
                )
            except Exception:
                pass

        sys.excepthook = _hook  # type: ignore[assignment]
