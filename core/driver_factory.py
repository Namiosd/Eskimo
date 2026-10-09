from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.options import ArgOptions
import time
from config.config import TestConfig
from core.logger import logger


class AppiumOptions(ArgOptions):
    """Custom wrapper for Appium capabilities initialization."""
    @property
    def default_capabilities(self) -> dict:
        return {}


def create_driver() -> webdriver.Remote:
    """Connect Appium Remote Session to the target emulator device."""
    options = AppiumOptions()
    for k, v in TestConfig.get_desired_capabilities().items():
        options.set_capability(k, v)
        
    driver = webdriver.Remote(TestConfig.APPIUM_URL, options=options)
    logger.info("Connected to Appium Server and initialized Android session successfully.")
    return driver


def check_and_dismiss_anr(driver: webdriver.Remote) -> None:
    """Detect and automatically dismiss Android system ANR dialogs if present."""
    try:
        anr_btn = driver.find_element(AppiumBy.ID, "android:id/aerr_wait")
        if anr_btn.is_displayed():
            anr_btn.click()
            logger.warning("System ANR dialog detected! Clicked 'Wait' to let application load.")
            time.sleep(4)
    except Exception:
        pass
