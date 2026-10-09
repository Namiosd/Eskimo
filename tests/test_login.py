import pytest
import allure
from pages.login_page import login
from core.logger import logger


@allure.feature("Authentication Gate")
@allure.story("Login using Mobile Number from Onboarding/Start Screen")
@allure.severity(allure.severity_level.CRITICAL)
def test_login_home(driver) -> None:
    """
    TC_LOGIN_HOME: Login using the onboarding Home screen option.
    Uses the raw driver fixture.
    """
    logger.info("Executing TC_LOGIN_HOME...")
    login(driver)
    logger.info("TC_LOGIN_HOME - PASSED!")
