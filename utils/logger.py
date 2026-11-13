import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


PARENT_LOGGER_NAME = "appium_framework"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_RUN_LOG_DIR: Optional[Path] = None


class AnsiColorFormatter(logging.Formatter):
    """Console formatter adding ANSI colors to log levels while keeping the structured pipe format."""

    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[1;31m" # Bold Red
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str = LOG_FORMAT, datefmt: str = DATE_FORMAT, use_color: bool = True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        if not self.use_color:
            return formatted
        color = self.COLORS.get(record.levelno, "")
        if color:
            return f"{color}{formatted}{self.RESET}"
        return formatted


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter supporting structured key-value pairs via `kv={...}`:
        logger.info("TEST START", kv={"test": item.name, "module": mod, "platform": "android"})
    Produces:
        2026-11-12 14:55:01 | INFO     | appium_framework | TEST START | test=test_login module=test_login platform=android
    """

    def process(self, msg: Any, kwargs: Dict[str, Any]):
        kv: Optional[Dict[str, Any]] = kwargs.pop("kv", None)
        if kv and isinstance(kv, dict):
            kv_parts = []
            for k, v in kv.items():
                if v is None:
                    continue
                val_str = str(v)
                if " " in val_str and not (val_str.startswith("'") or val_str.startswith('"')):
                    kv_parts.append(f"{k}='{val_str}'")
                else:
                    kv_parts.append(f"{k}={val_str}")
            if kv_parts:
                msg = f"{msg} | {' '.join(kv_parts)}"
        return msg, kwargs


def _get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def init_run_log_dir(base_dir: Optional[Path] = None, run_stamp: Optional[str] = None) -> Path:
    """
    Create or attach to `logs/<YYYYMMDD_HHMMSS>/` and its subdirectories:
      - screenshots/
      - page_source/
      - suite.log
      - appium_server.log
    """
    global _RUN_LOG_DIR

    if _RUN_LOG_DIR is not None and _RUN_LOG_DIR.exists():
        return _RUN_LOG_DIR

    env_dir = os.environ.get("ESKIMO_RUN_LOG_DIR")
    if env_dir:
        run_dir = Path(env_dir).resolve()
    else:
        root = Path(base_dir) if base_dir else _get_project_root()
        stamp = run_stamp or os.environ.get("ESKIMO_RUN_STAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")
        os.environ["ESKIMO_RUN_STAMP"] = stamp
        run_dir = (root / "logs" / stamp).resolve()
        os.environ["ESKIMO_RUN_LOG_DIR"] = str(run_dir)

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "screenshots").mkdir(parents=True, exist_ok=True)
    (run_dir / "page_source").mkdir(parents=True, exist_ok=True)

    # Touch appium_server.log and suite.log so they always exist inside logs/<run_stamp>/
    appium_log = run_dir / "appium_server.log"
    if not appium_log.exists():
        appium_log.touch()

    _RUN_LOG_DIR = run_dir
    _configure_parent_logger(run_dir / "suite.log")
    return run_dir


def get_run_log_dir() -> Path:
    """Return the active `logs/<YYYYMMDD_HHMMSS>/` directory, initializing it if needed."""
    if _RUN_LOG_DIR is None:
        return init_run_log_dir()
    return _RUN_LOG_DIR


def get_suite_log_path() -> Path:
    """Return the path to `logs/<YYYYMMDD_HHMMSS>/suite.log`."""
    return get_run_log_dir() / "suite.log"


def get_appium_log_path() -> Path:
    """Return the path to `logs/<YYYYMMDD_HHMMSS>/appium_server.log`."""
    return get_run_log_dir() / "appium_server.log"


def _configure_parent_logger(suite_log_path: Path) -> logging.Logger:
    """Configure the parent `appium_framework` logger with console + suite.log file handlers."""
    parent_logger = logging.getLogger(PARENT_LOGGER_NAME)
    parent_logger.setLevel(logging.INFO)
    parent_logger.propagate = False

    # Check existing handlers to avoid duplicate console/file handlers
    has_console = False
    has_file = False
    target_file_str = str(suite_log_path.resolve())

    for h in list(parent_logger.handlers):
        if isinstance(h, logging.FileHandler):
            if os.path.abspath(getattr(h, "baseFilename", "")) == target_file_str:
                has_file = True
            else:
                parent_logger.removeHandler(h)
                h.close()
        elif isinstance(h, logging.StreamHandler):
            has_console = True

    if not has_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(AnsiColorFormatter(LOG_FORMAT, DATE_FORMAT, use_color=True))
        parent_logger.addHandler(console_handler)

    if not has_file:
        file_handler = logging.FileHandler(suite_log_path, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        parent_logger.addHandler(file_handler)

    return parent_logger


def get_logger(name: Optional[str] = None) -> StructuredLoggerAdapter:
    """
    Return a StructuredLoggerAdapter bound to `appium_framework` (or child `appium_framework.<name>`).
    Ensures `logs/<run_stamp>/suite.log` is initialized.
    """
    init_run_log_dir()
    if not name or name == PARENT_LOGGER_NAME:
        full_name = PARENT_LOGGER_NAME
    elif name.startswith(f"{PARENT_LOGGER_NAME}."):
        full_name = name
    else:
        full_name = f"{PARENT_LOGGER_NAME}.{name}"

    base_logger = logging.getLogger(full_name)
    base_logger.setLevel(logging.INFO)
    return StructuredLoggerAdapter(base_logger, {})

