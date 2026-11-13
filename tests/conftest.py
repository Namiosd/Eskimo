import base64
import json
import logging
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
import pytest

# Add ESKIMO workspace directory root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.driver_factory import create_driver
from pages.login_page import login
from config import TestConfig
from utils.logger import (
    get_logger,
    init_run_log_dir,
    get_run_log_dir,
    get_suite_log_path,
    get_appium_log_path,
)
from utils.screenshot import capture_failure_artifacts

logger = get_logger("appium_framework")


# ============================================================
# PYTEST CLI OPTIONS
# ============================================================

def pytest_addoption(parser):
    """Register custom CLI options for locale and platform."""
    try:
        parser.addoption("--locale", action="store", default="en", help="Test locale (default: en)")
    except ValueError:
        pass
    try:
        parser.addoption("--platform", action="store", default="android", help="Target platform (default: android)")
    except ValueError:
        pass


def _sanitize_test_name(node) -> str:
    """Build a safe filename suffix from pytest item (e.g. TestClass_test_name or test_name)."""
    cls_name = node.cls.__name__ if getattr(node, "cls", None) else ""
    raw = f"{cls_name}_{node.name}" if cls_name else node.name
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("_")


def _query_appium_version(appium_url: str) -> str:
    """Query Appium `/status` endpoint to retrieve server build version."""
    status_url = f"{appium_url.rstrip('/')}/status"
    try:
        with urllib.request.urlopen(status_url, timeout=3) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            # Append status payload to appium_server.log for diagnostics
            try:
                appium_log = get_appium_log_path()
                with open(appium_log, "a", encoding="utf-8") as f:
                    f.write(f"[Appium /status] {raw}\n")
            except Exception:
                pass
            data = json.loads(raw)
            build_info = data.get("value", {}).get("build", {})
            return str(build_info.get("version", "2.x"))
    except Exception:
        return "2.x"


# ============================================================
# SESSION LIFECYCLE HOOKS
# ============================================================

def pytest_sessionstart(session):
    """
    Initialize `logs/<YYYYMMDD_HHMMSS>/` directory and emit structured session start events:
      - Target | summary=platform=android device_name='<name>' udid=<udid> ...
      - Appium server started successfully | ... version=<ver>
    """
    run_dir = init_run_log_dir()
    session._run_log_dir = run_dir
    session._counts = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}

    platform = session.config.getoption("--platform", default="android")
    locale = session.config.getoption("--locale", default="en")
    device_name = TestConfig.DEVICE_NAME
    udid = TestConfig.DEVICE_NAME
    app_pkg = TestConfig.APP_PACKAGE

    target_summary = (
        f"platform={platform} device_name='{device_name}' udid={udid} "
        f"app_package={app_pkg} locale={locale}"
    )
    logger.info(f"Target | summary={target_summary}")

    appium_ver = _query_appium_version(TestConfig.APPIUM_URL)
    logger.info(
        "Appium server started successfully",
        kv={
            "url": TestConfig.APPIUM_URL,
            "version": appium_ver,
            "appium_log": str(get_appium_log_path()),
        },
    )


def pre_check_environment() -> None:
    """Validate system environment settings (Appium port and adb connectivity)."""
    logger.info("Verifying test automation runtime environment setup...")

    # 1. Verify Appium Server port connectivity
    appium_host = "127.0.0.1"
    appium_port = 4723
    appium_online = False
    try:
        with socket.create_connection((appium_host, appium_port), timeout=2):
            appium_online = True
    except OSError:
        appium_online = False

    if not appium_online:
        pytest.exit(
            f"\n\n❌ ENVIRONMENT ERROR: Appium Server is not running at http://{appium_host}:{appium_port}!\n"
            f"👉 Please start Appium by double-clicking 'start.bat' or running 'appium' in a new command prompt.\n",
            returncode=1
        )
    logger.info("Appium Server connection verified (Active).")

    # 2. Verify Emulator Online Status
    device_id = TestConfig.DEVICE_NAME
    emulator_online = False
    adb_installed = True
    try:
        result = subprocess.run(
            ["adb", "devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if device_id in result.stdout:
            for line in result.stdout.splitlines():
                if device_id in line:
                    if "device" in line and "offline" not in line:
                        emulator_online = True
                        break
    except FileNotFoundError:
        adb_installed = False

    if not adb_installed:
        logger.warning("adb command utility not found in PATH system environment variable.")
    elif not emulator_online:
        pytest.exit(
            f"\n\n❌ ENVIRONMENT ERROR: Targeted virtual device '{device_id}' is offline or disconnected!\n"
            f"👉 Please open Android Studio and boot virtual device '{device_id}' to active Home layout state.\n",
            returncode=1
        )
    else:
        logger.info(f"Target emulator device '{device_id}' verified (Online).")


# ============================================================
# VIDEO RECORDING HELPERS (Appium start_recording_screen + ADB fallback)
# ============================================================

def _start_adb_screenrecord_fallback(item) -> None:
    """Start adb screenrecord on device as fallback in case Appium recording is unavailable."""
    device_id = TestConfig.DEVICE_NAME
    remote_path = f"/sdcard/rec_{_sanitize_test_name(item)}.mp4"
    item._remote_video_path = remote_path
    item._adb_rec_proc = None
    try:
        subprocess.run(
            ["adb", "-s", device_id, "shell", "rm", "-f", remote_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        proc = subprocess.Popen(
            ["adb", "-s", device_id, "shell", "screenrecord", "--bit-rate", "4000000", remote_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        item._adb_rec_proc = proc
    except Exception as exc:
        logger.debug(f"ADB screenrecord fallback not started: {exc}")


def _stop_and_save_video(item, driver_instance=None) -> None:
    """
    Stop screen recording and write `.mp4` file to `logs/<run_stamp>/video_<TestName>.mp4`.
    Prefers `driver.stop_recording_screen()` base64 output; falls back to pulling ADB screenrecord.
    """
    if getattr(item, "_video_saved", False):
        return

    video_path: Path = getattr(item, "_video_path", None)
    if not video_path:
        return

    # 1. Try Appium native stop_recording_screen() if driver session is active
    drv = driver_instance or getattr(item, "driver", None)
    if drv and getattr(item, "_appium_recording_active", False):
        try:
            b64_data = drv.stop_recording_screen()
            item._appium_recording_active = False
            if b64_data:
                video_bytes = base64.b64decode(b64_data)
                if len(video_bytes) > 0:
                    video_path.write_bytes(video_bytes)
                    item._video_saved = True
                    logger.info(f"Video recording saved via Appium: {video_path}")
        except Exception as exc:
            logger.debug(f"Appium stop_recording_screen fallback notice: {exc}")

    # 2. Stop ADB fallback recorder and pull if video_path is not yet saved
    proc = getattr(item, "_adb_rec_proc", None)
    remote_path = getattr(item, "_remote_video_path", None)
    device_id = TestConfig.DEVICE_NAME

    if proc is not None:
        try:
            subprocess.run(
                ["adb", "-s", device_id, "shell", "pkill", "-l", "INT", "screenrecord"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            pass
        item._adb_rec_proc = None

    if not getattr(item, "_video_saved", False) and remote_path:
        try:
            time.sleep(1)  # Allow mp4 moov atom to flush on Android
            subprocess.run(
                ["adb", "-s", device_id, "pull", remote_path, str(video_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
            )
            if video_path.exists() and video_path.stat().st_size > 0:
                item._video_saved = True
                logger.info(f"Video recording saved via ADB screenrecord: {video_path}")
        except Exception as exc:
            logger.warning(f"Could not pull fallback video recording: {exc}")

    if remote_path:
        try:
            subprocess.run(
                ["adb", "-s", device_id, "shell", "rm", "-f", remote_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
        except Exception:
            pass


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope="function")
def driver(request):
    """Function-scoped fixture creating a fresh Appium Remote Session for each testcase."""
    pre_check_environment()

    logger.info("Initializing fresh function-scoped Appium remote session...")
    driver_instance = create_driver()
    request.node.driver = driver_instance

    # Start Appium native screen recording on the active driver session
    try:
        driver_instance.start_recording_screen()
        request.node._appium_recording_active = True
    except Exception as exc:
        request.node._appium_recording_active = False
        logger.debug(f"driver.start_recording_screen() not active, starting ADB fallback: {exc}")
        _start_adb_screenrecord_fallback(request.node)

    yield driver_instance

    # Stop Appium screen recording before quitting driver session
    _stop_and_save_video(request.node, driver_instance)

    logger.info("Closing Appium remote session...")
    try:
        driver_instance.quit()
        logger.info("Appium remote session terminated safely.")
    except Exception as e:
        logger.error(f"Error encountered while closing Appium session: {e}")


@pytest.fixture(scope="function", autouse=True)
def ensure_app_active(driver):
    """Autouse fixture ensuring application foreground state before each test execution."""
    app_package = TestConfig.APP_PACKAGE
    try:
        app_state = driver.query_app_state(app_package)
        if app_state == 4:
            logger.info(f"Application package {app_package} is already active in the foreground. Skipping activation.")
            return

        logger.info(f"Application package {app_package} (state={app_state}) is not in foreground. Activating to active foreground...")
        driver.activate_app(app_package)
        time.sleep(5)
    except Exception as e:
        logger.error(f"Force application activation failed: {e}")


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """Function-scoped fixture ensuring authenticated credentials session state before test cases."""
    logger.info("Synchronizing pre-test authenticated session state...")
    login(driver)
    yield driver


@pytest.fixture(scope="function", autouse=True)
def step_tracker_fixture(request):
    """Automatically initialize StepTracker for each test and print execution summary."""
    from core.step_tracker import StepTracker, set_current_tracker
    tracker = StepTracker(request.node.name)
    set_current_tracker(tracker)
    yield tracker
    tracker.print_summary()
    set_current_tracker(None)


# ============================================================
# RUNTEST HOOKS (SETUP, MAKEREPORT, SESSIONFINISH)
# ============================================================

def pytest_runtest_setup(item):
    """
    Hook executed at the start of each test:
      1. Log `TEST START | test=<item.name> module=<module> platform=android`
      2. Start screen recording and log `Video recording started | video=<path>`
    """
    run_dir = get_run_log_dir()
    platform = item.config.getoption("--platform", default="android")
    module_name = item.module.__name__ if getattr(item, "module", None) else "unknown_module"

    logger.info(
        "TEST START",
        kv={
            "test": item.name,
            "module": module_name,
            "platform": platform,
        },
    )

    safe_test = _sanitize_test_name(item)
    video_path = run_dir / f"video_{safe_test}.mp4"
    item._video_path = video_path
    item._video_saved = False
    item._adb_rec_proc = None

    logger.info("Video recording started", kv={"video": str(video_path)})


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Lifecycle report hook:
      - When `call.when == 'call'`:
          * If failed: log `Error Captured: <call.excinfo.value>` and capture screenshot + XML page_source
          * Log `TEST FINISH | test=<item.name> outcome=<passed|failed> duration_s=<seconds>`
      - When `call.when == 'teardown'`:
          * Ensure Android screen recording is stopped and saved to `logs/<run_stamp>/video_<TestName>.mp4`
    """
    outcome = yield
    rep = outcome.get_result()

    if call.when == "call":
        platform = item.config.getoption("--platform", default="android")
        locale = item.config.getoption("--locale", default="en")
        duration_s = f"{rep.duration:.2f}"

        # Update session counters
        counts = getattr(item.session, "_counts", None)
        if counts is not None:
            if rep.passed:
                counts["passed"] += 1
            elif rep.failed:
                counts["failed"] += 1
            elif rep.skipped:
                counts["skipped"] += 1

        if rep.failed:
            err_msg = str(call.excinfo.value).replace("\n", " ").strip() if call.excinfo else "Test assertion or runtime error"
            logger.error(f"Error Captured: {err_msg}")

            driver_instance = getattr(item, "driver", None)
            if not driver_instance:
                if "logged_in_driver" in item.funcargs:
                    driver_instance = item.funcargs["logged_in_driver"]
                elif "driver" in item.funcargs:
                    driver_instance = item.funcargs["driver"]

            screenshot_path, page_source_path = capture_failure_artifacts(
                driver=driver_instance,
                test_name=item.name,
                platform=platform,
                locale=locale,
                run_dir=get_run_log_dir(),
            )

            # Attach to Allure if available (best-effort)
            try:
                import allure
                if screenshot_path and screenshot_path.exists():
                    allure.attach(
                        screenshot_path.read_bytes(),
                        name="Failure Screenshot",
                        attachment_type=allure.attachment_type.PNG,
                    )
                if page_source_path and page_source_path.exists():
                    allure.attach(
                        page_source_path.read_text(encoding="utf-8"),
                        name="Failure Page Source XML",
                        attachment_type=allure.attachment_type.XML,
                    )
            except Exception:
                pass

        outcome_str = "passed" if rep.passed else ("skipped" if rep.skipped else "failed")
        logger.info(
            "TEST FINISH",
            kv={
                "test": item.name,
                "outcome": outcome_str,
                "duration_s": duration_s,
            },
        )

    elif call.when == "setup" and rep.failed:
        counts = getattr(item.session, "_counts", None)
        if counts is not None:
            counts["error"] += 1
        err_msg = str(call.excinfo.value).replace("\n", " ").strip() if call.excinfo else "Setup error"
        logger.error(f"Error Captured: {err_msg}")
        logger.info(
            "TEST FINISH",
            kv={
                "test": item.name,
                "outcome": "failed",
                "duration_s": f"{rep.duration:.2f}",
            },
        )

    elif call.when == "teardown":
        # Finalize video recording if not already stopped before driver.quit()
        _stop_and_save_video(item, getattr(item, "driver", None))


def pytest_sessionfinish(session, exitstatus):
    """
    Emit structured session summary log and automatically generate `logs/<run_stamp>/report.html`
    alongside existing HTML diagnostic reports.
    """
    counts = getattr(session, "_counts", {"passed": 0, "failed": 0, "skipped": 0, "error": 0})
    suite_log = get_suite_log_path()
    run_dir = get_run_log_dir()

    logger.info(
        "Test session finished",
        kv={
            "exitstatus": int(exitstatus),
            "passed": counts["passed"],
            "failed": counts["failed"],
            "skipped": counts["skipped"],
            "error": counts["error"],
            "suite_log": str(suite_log),
        },
    )

    # Flush file handlers before parsing suite.log
    for h in logging.getLogger("appium_framework").handlers:
        try:
            h.flush()
        except Exception:
            pass

    # Automatically generate `logs/<run_stamp>/report.html` from `suite.log`
    try:
        from generate_report import generate_html_report
        report_out = run_dir / "report.html"
        generate_html_report(suite_log, report_out)
        logger.info(f"Generated standalone run report: {report_out}")
    except Exception as exc:
        logger.warning(f"Could not auto-generate logs/<run_stamp>/report.html: {exc}")

    # Legacy post-test HTML diagnostic reports
    try:
        from scripts.export_failed_report import export_failed_report
        export_failed_report()
    except Exception:
        pass

    try:
        from scripts.generate_defects_report import export_defects_html
        export_defects_html()
    except Exception:
        pass

    try:
        from pages.ai_agent_page import ChatTranscript
        ChatTranscript.export_html_report()
    except Exception:
        pass
