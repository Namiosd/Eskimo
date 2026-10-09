import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from core.logger import logger
from core.driver_factory import check_and_dismiss_anr


def wait_for_element_with_anr_handling(
    driver: webdriver.Remote, 
    xpath: str, 
    timeout: int = 60
) -> webdriver.WebElement:
    """
    Safely wait for an element to appear, continuously dismisses system ANR popups.
    
    Args:
        driver: Remote Appium WebDriver instance.
        xpath: Target element XPath selector.
        timeout: Maximum wait time in seconds.
        
    Returns:
        The matched WebElement once it becomes visible.
    """
    end_time = time.monotonic() + timeout
    logger.info(f"Waiting for element '{xpath}' up to {timeout}s (ANR filtering enabled)...")
    while time.monotonic() < end_time:
        check_and_dismiss_anr(driver)
        
        try:
            element = driver.find_element(AppiumBy.XPATH, xpath)
            if element.is_displayed():
                return element
        except Exception:
            pass
            
        time.sleep(2)
        
    raise TimeoutException(f"Timed out waiting for element XPath '{xpath}' after {timeout} seconds.")


def handle_notification_onboarding(driver: webdriver.Remote) -> None:
    """Handle post-login notification permission request overlays by clicking Allow or Skip."""
    try:
        wait = WebDriverWait(driver, 5)
        allow_or_skip = wait.until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//*[@resource-id='travel.eskimo.esim.uat:id/btn_allow'] | //*[@resource-id='travel.eskimo.esim.uat:id/btn_skip']"
            ))
        )
        allow_or_skip.click()
        logger.info("Clicked 'Allow' or 'Skip' on the Notification Onboarding screen.")
        time.sleep(2)
        
        # Confirm system permission popups
        try:
            allow_system_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button"))
            )
            allow_system_btn.click()
            logger.info("Confirmed OS system permission request.")
            time.sleep(2)
        except Exception:
            pass
    except Exception as e:
        logger.info(f"No notification onboarding overlay detected: {e}")


def handle_welcome_popup(driver: webdriver.Remote) -> None:
    """Close post-login introductory marketing or welcome sheets."""
    try:
        wait = WebDriverWait(driver, 5)
        popup_present = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Welcome') or contains(@text, 'Refer a friend')]"))
        )
        if popup_present:
            logger.info("Introductory popup detected. Resolving close locator...")
            close_locators = [
                (AppiumBy.ID, "travel.eskimo.esim.uat:id/img_close"),
                (AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_close"),
                (AppiumBy.ID, "travel.eskimo.esim.uat:id/iv_close"),
                (AppiumBy.XPATH, "//android.widget.FrameLayout[@resource-id='travel.eskimo.esim.uat:id/design_bottom_sheet']//android.widget.ImageView[@clickable='true']"),
                (AppiumBy.XPATH, "//*[contains(@text, 'Welcome')]/preceding-sibling::android.widget.ImageView"),
                (AppiumBy.XPATH, "//*[contains(@text, 'Welcome')]/following-sibling::android.widget.ImageView")
            ]
            for locator in close_locators:
                try:
                    close_btn = driver.find_element(*locator)
                    if close_btn.is_displayed():
                        close_btn.click()
                        logger.info("Closed intro popup successfully.")
                        time.sleep(1)
                        return
                except Exception:
                    continue
            logger.warning("Could not close introductory popup using preset locators.")
    except Exception:
        logger.info("No introductory popup detected.")
