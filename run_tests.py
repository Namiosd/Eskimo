import argparse
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from utils.logger import init_run_log_dir, get_logger, get_appium_log_path


def _is_appium_listening(host: str = "127.0.0.1", port: int = 4723) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def _ensure_appium_server(appium_log_path: Path):
    """
    Ensure Appium Server is running on 127.0.0.1:4723.
    If not running, start Appium in the background redirecting stdout/stderr to `appium_server.log`.
    """
    if _is_appium_listening():
        with open(appium_log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Appium Server already active on 127.0.0.1:4723\n")
        return None

    log_file = open(appium_log_path, "a", encoding="utf-8")
    cmd = ["appium.cmd" if os.name == "nt" else "appium", "--address", "127.0.0.1", "--port", "4723"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            shell=(os.name == "nt"),
        )
        for _ in range(15):
            if _is_appium_listening():
                break
            time.sleep(1)
        return proc
    except Exception as exc:
        log_file.write(f"Failed to auto-start Appium server: {exc}\n")
        log_file.flush()
        return None


def _resolve_target_path(project_root: Path, target: str) -> str:
    if not target:
        return str(project_root / "tests")
    candidate = Path(target)
    if candidate.exists():
        return str(candidate)
    in_root = project_root / target
    if in_root.exists():
        return str(in_root)
    in_tests = project_root / "tests" / target
    if in_tests.exists():
        return str(in_tests)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Android Pytest + Appium suite with timestamped structured logging")
    parser.add_argument("--target", default="tests", help="Target test file, node id, or directory")
    parser.add_argument("--locale", default="en", help="Test locale (default: en)")
    parser.add_argument("--platform", default="android", help="Target platform (default: android)")
    args, extra_args = parser.parse_known_args()

    project_root = Path(__file__).resolve().parent
    run_dir = init_run_log_dir(base_dir=project_root)
    os.environ["ESKIMO_RUN_LOG_DIR"] = str(run_dir)

    logger = get_logger("appium_framework.runner")
    appium_proc = _ensure_appium_server(get_appium_log_path())

    resolved_target = _resolve_target_path(project_root, args.target)
    pytest_args = [
        resolved_target,
        f"--locale={args.locale}",
        f"--platform={args.platform}",
        "-v",
        "-s",
        *extra_args,
    ]

    logger.info(
        "Starting Pytest execution",
        kv={"target": resolved_target, "run_dir": str(run_dir)},
    )

    try:
        import pytest
        exit_code = pytest.main(pytest_args)
    finally:
        if appium_proc is not None:
            try:
                appium_proc.terminate()
            except Exception:
                pass

    return int(exit_code)


if __name__ == "__main__":
    sys.exit(main())

