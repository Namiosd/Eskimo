import os
import sys
import pytest
import time
import socket
import subprocess

# Add workspace directory root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.driver_factory import create_driver
from pages.login_page import login
from config import TestConfig
from core.logger import logger


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


@pytest.fixture(scope="function")
def driver(request):
    """Function-scoped fixture creating a fresh Appium Remote Session for each testcase."""
    pre_check_environment()

    logger.info("Initializing fresh function-scoped Appium remote session...")
    driver_instance = create_driver()
    request.node.driver = driver_instance
    yield driver_instance
    
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
        # Check if the app is already in the foreground (4 = running in foreground)
        app_state = driver.query_app_state(app_package)
        if app_state == 4:
            logger.info(f"Application package {app_package} is already active in the foreground. Skipping activation.")
            return

        logger.info(f"Application package {app_package} (state={app_state}) is not in foreground. Activating to active foreground...")
        driver.activate_app(app_package)
        time.sleep(5)  # Await app render transition
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Post-mortem hook creating diagnostic reports (screenshot + DOM page source) on test case failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.failed:
        try:
            driver_instance = getattr(item, "driver", None)
            if not driver_instance:
                if "logged_in_driver" in item.funcargs:
                    driver_instance = item.funcargs["logged_in_driver"]
                elif "driver" in item.funcargs:
                    driver_instance = item.funcargs["driver"]
                
            if driver_instance:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                screenshots_dir = os.path.join(base_dir, "reports", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)

                screenshot_path = os.path.join(screenshots_dir, "debug_failure.png")
                driver_instance.save_screenshot(screenshot_path)
                logger.error(f"Test case failed! Saved diagnostic viewport screenshot to: {os.path.abspath(screenshot_path)}")
                
                source_path = os.path.join(screenshots_dir, "debug_page_source.xml")
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(driver_instance.page_source)
                logger.error(f"Saved diagnostic layout view DOM source to: {os.path.abspath(source_path)}")

                try:
                    import allure
                    allure.attach(
                        driver_instance.get_screenshot_as_png(),
                        name="Failure Screenshot",
                        attachment_type=allure.attachment_type.PNG
                    )
                    allure.attach(
                        driver_instance.page_source,
                        name="Failure Page Source XML",
                        attachment_type=allure.attachment_type.XML
                    )
                    logger.info("Successfully attached failure diagnostics to Allure report.")
                except ImportError:
                    logger.warning("allure module not available. Skipping Allure attachments.")
        except Exception as e:
            logger.error(f"Unable to capture diagnostics details for current session: {e}")
