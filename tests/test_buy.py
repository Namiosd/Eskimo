import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.buy_data_page import buy_data_plan
from core.logger import logger


def test_buy_data_from_home(logged_in_driver) -> None:
    """
    Test case purchasing data plan package starting from the Home tab.
    """
    logger.info("Executing test_buy_data_from_home...")
    buy_data_plan(logged_in_driver)
    logger.info("test_buy_data_from_home - PASSED!")


@pytest.mark.skip(reason="Obsolete: Data tab/Wifi tab removed in new version of Eskimo UAT")
def test_buy_data_from_dashboard(logged_in_driver) -> None:
    """
    Test case purchasing data plan starting from the Data Dashboard.
    """
    logger.info("Executing test_buy_data_from_dashboard...")
    wait = WebDriverWait(logged_in_driver, 15)
    
    # 1. Access Data Tab
    data_tab = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_wifi"))
    )
    data_tab.click()
    logger.info("Accessed Data Dashboard tab view.")
    time.sleep(2)

    # 2. Click Buy on Dashboard card
    buy_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/buy_image_card"))
    )
    assert buy_btn.is_displayed(), "Dashboard card buy redirection button is not visible!"
    buy_btn.click()
    logger.info("Redirection button clicked. Navigated back to Home tab.")
    time.sleep(2)

    # 3. Proceed standard checkout flow
    buy_data_plan(logged_in_driver)
    logger.info("test_buy_data_from_dashboard - PASSED!")
