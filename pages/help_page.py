import time
import allure
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

from core.logger import logger
from core.step_tracker import Step
from pages.base_page import wait_for_element_with_anr_handling

BTN_HELP_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/help_image_card']"
HELP_CENTER_TITLE_XPATH = '//android.widget.TextView[@text="HELP CENTER"]'


def click_help(driver: webdriver.Remote) -> None:
    """
    Click nút Help và verify màn hình Help Center hiển thị.
    Dùng được ở bất kỳ màn hình nào có nút Help.
    Pattern: Check UI → Action → Verify
    """
    with allure.step("Check UI - Help button visibility"), Step("Check UI - Help button visibility"):
        help_btn = wait_for_element_with_anr_handling(driver, BTN_HELP_XPATH, timeout=15)
        assert help_btn.is_displayed(), "❌ [Help] Không thấy nút Help!"
        logger.info("Check UI: Help button is displayed.")

    with allure.step("Action - Click Help button"), Step("Action - Click Help button"):
        help_btn.click()
        logger.info("Action: Clicked Help button.")

    with allure.step("Verify - Help Center page is displayed"), Step("Verify - Help Center page is displayed"):
        time.sleep(2)
        help_title = wait_for_element_with_anr_handling(driver, HELP_CENTER_TITLE_XPATH, timeout=15)
        assert help_title.is_displayed(), "❌ [Help] Không thấy màn hình Help Center!"
        logger.info("Verify: Help Center page is displayed.")
