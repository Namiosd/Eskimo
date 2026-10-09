from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import allure

from config.config import TestConfig
from core.logger import logger
from core.step_tracker import Step
from core.driver_factory import create_driver, check_and_dismiss_anr
from pages.base_page import (
    wait_for_element_with_anr_handling,
    handle_notification_onboarding,
    handle_welcome_popup
)


def _tap_login_on_sign_up(driver: webdriver.Remote, text_element: webdriver.WebElement) -> None:
    """Helper method to click the nested 'Log in' text segment inside the Sign Up description."""
    location = text_element.location
    size = text_element.size
    x = int(location['x'] + size['width'] * 0.85)
    y = int(location['y'] + size['height'] / 2)
    driver.tap([(x, y)])
    time.sleep(2)


def _execute_mobile_number_login(driver: webdriver.Remote, phone: str, otp: str) -> None:
    """Perform mobile number input, OTP verification, and post-login resolution stages."""
    wait = WebDriverWait(driver, 20)
    
    # 4. Select Country Code (Vietnam)
    with allure.step("Select Vietnam country code (+84)"), Step("Select Vietnam country code (+84)"):
        for _ in range(3):
            try:
                country_code = wait.until(
                    EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
                )
                country_code.click()
                break
            except StaleElementReferenceException:
                time.sleep(1)
        time.sleep(1)

        search_field = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txtSearch"))
        )
        search_field.send_keys(TestConfig.COUNTRY_SEARCH)
        time.sleep(1)

        vietnam_option = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH,
                '//android.widget.RelativeLayout[@resource-id="travel.eskimo.esim.uat:id/test"]/android.widget.LinearLayout/android.widget.LinearLayout'))
        )
        vietnam_option.click()

    # 5. Enter Phone Number
    with allure.step(f"Enter phone number: {phone}"), Step(f"Enter phone number: {phone}"):
        phone_field = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
        )
        phone_field.clear()
        phone_field.send_keys(phone)
        logger.info(f"Entered phone number: {phone}")

        # Click Continue
        continue_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_continue"))
        )
        continue_btn.click()

    # 6. Request OTP via WhatsApp
    with allure.step("Request OTP via WhatsApp channel"), Step("Request OTP via WhatsApp channel"):
        whatsapp_btn = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_whatsapp"))
        )
        whatsapp_btn.click()
        logger.info("OTP requested via WhatsApp channel.")

    # 7. Populate OTP digits
    with allure.step(f"Input OTP code: {otp}"), Step(f"Input OTP code: {otp}"):
        time.sleep(6)
        wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/otp1"))
        )
        for i, digit in enumerate(otp, start=1):
            otp_field = driver.find_element(AppiumBy.ID, f"travel.eskimo.esim.uat:id/otp{i}")
            otp_field.send_keys(digit)
        logger.info(f"Submitted OTP code: {otp}")

    # 8. Clear system prompts/marketing popups & Verify Login
    with allure.step("Dismiss onboarding popups and verify home tab visibility"), Step("Dismiss onboarding popups and verify home tab visibility"):
        handle_notification_onboarding(driver)
        handle_welcome_popup(driver)

        time.sleep(2)
        home_tab = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home']", timeout=60)
        assert home_tab.is_displayed(), "Home screen navigation check failed after login sequence!"
        logger.info("Authentication complete. Home screen dashboard is fully loaded.")


def login(driver: webdriver.Remote, phone: str = TestConfig.PHONE_NUMBER, otp: str = TestConfig.OTP) -> None:
    """Login flow starting directly from the default start screen/onboarding screen."""
    wait = WebDriverWait(driver, 20)
    logger.info("Analyzing startup screen layout...")
    
    # Handle notification onboarding & welcome popups if app opens directly with them
    handle_notification_onboarding(driver)
    handle_welcome_popup(driver)
    
    # Recovery stage: If app is open on an inner screen, tap back button to return to home/login gate
    for i in range(3):
        try:
            # Wait up to 6 seconds for either main screen targets or a back button to appear
            detect_xpath = (
                "//*[@resource-id='travel.eskimo.esim.uat:id/txt_login'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/tv_explore_plans'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/lbl_sign_up'] | "
                "//android.widget.TextView[@text='Welcome back'] | "
                "//android.widget.TextView[@text='Continue with Mobile Number'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/btn_allow'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/btn_skip'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/back'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/btn_back'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/img_back'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/btnBack'] | "
                "//*[@resource-id='travel.eskimo.esim.uat:id/btnCloseChat']"
            )
            element = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((AppiumBy.XPATH, detect_xpath))
            )
            
            # Check what element was matched
            resource_id = element.get_attribute("resource-id") or ""
            if any(b in resource_id for b in ["back", "btn_back", "img_back", "btnBack", "btnCloseChat"]):
                logger.info(f"App is on an inner page (attempt {i+1}/3, found {resource_id}). Tapping back to recover to home/login view...")
                element.click()
                time.sleep(2)
            elif resource_id in ["travel.eskimo.esim.uat:id/btn_allow", "travel.eskimo.esim.uat:id/btn_skip"]:
                handle_notification_onboarding(driver)
                time.sleep(2)
            else:
                logger.info("Found onboarding/login/home options on current view screen.")
                break
        except Exception as e:
            logger.info(f"Recovery scan attempt {i+1}/3: {e}")
            try:
                driver.back()
                time.sleep(2)
            except Exception:
                break
    
    xpath_targets = (
        "//*[@resource-id='travel.eskimo.esim.uat:id/txt_login'] | "
        "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home'] | "
        "//*[@resource-id='travel.eskimo.esim.uat:id/tv_explore_plans'] | "
        "//*[@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer'] | "
        "//*[@resource-id='travel.eskimo.esim.uat:id/lbl_sign_up'] | "
        "//android.widget.TextView[@text='Welcome back'] | "
        "//android.widget.TextView[@text='Continue with Mobile Number'] | "
        "//*[@resource-id='travel.eskimo.esim.uat:id/btn_allow'] | "
        "//*[@resource-id='travel.eskimo.esim.uat:id/btn_skip']"
    )
    
    try:
        # Load startup element with integrated system ANR protection
        loaded_element = wait_for_element_with_anr_handling(driver, xpath_targets, timeout=60)
        
        # Safeguard layout redraw updates
        for _ in range(3):
            try:
                resource_id = loaded_element.get_attribute("resource-id")
                text = loaded_element.text
                break
            except StaleElementReferenceException:
                time.sleep(1)
                loaded_element = driver.find_element(AppiumBy.XPATH, xpath_targets)
                
        # Handle current layout state
        if resource_id in ["travel.eskimo.esim.uat:id/btn_allow", "travel.eskimo.esim.uat:id/btn_skip"]:
            handle_notification_onboarding(driver)
            time.sleep(2)
            loaded_element = wait_for_element_with_anr_handling(driver, xpath_targets, timeout=30)
            resource_id = loaded_element.get_attribute("resource-id")

        if resource_id == "travel.eskimo.esim.uat:id/navigation_home":
            logger.info("Session is already authenticated. Clicking Home tab to synchronize.")
            try:
                loaded_element.click()
                time.sleep(2)
            except Exception:
                pass
            return
            
        elif resource_id in ["travel.eskimo.esim.uat:id/tv_explore_plans", "travel.eskimo.esim.uat:id/btn_claim_offer"]:
            logger.info("Currently on Guest Onboarding screen. Accessing authentication gate...")
            claim_btn = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_claim_offer")))
            claim_btn.click()
            time.sleep(3)
            
        else:
            logger.info("Directly on Sign up or Welcome back gate.")
            
    except Exception as e:
        raise Exception(f"Unable to recognize target login gate screen layout state: {e}")

    # 1. Check layout UI trước khi click
    with allure.step("Verify UI Layout: Check 'Continue with Mobile Number' button is visible and active"), Step("Verify UI Layout: Check 'Continue with Mobile Number' button is visible and active"):
        mobile_btn = wait_for_element_with_anr_handling(driver, "//*[@text='Continue with Mobile Number']", timeout=60)
        assert mobile_btn.is_displayed(), "UI ERROR: 'Continue with Mobile Number' button is not visible on login screen!"
        assert mobile_btn.is_enabled(), "UI ERROR: 'Continue with Mobile Number' button is disabled!"
        logger.info("UI Check: 'Continue with Mobile Number' button is displayed and active.")

    # 2. Bấm nút function
    with allure.step("Click 'Continue with Mobile Number' button"), Step("Click 'Continue with Mobile Number' button"):
        mobile_btn.click()
        logger.info("Clicked 'Continue with Mobile Number' button.")
    
    # 3. Verify xem sau khi bấm nút thì nút có hoạt động không
    with allure.step("Verify Transition: Check if phone number input field/country code is rendered"), Step("Verify Transition: Check if phone number input field/country code is rendered"):
        try:
            wait.until(
                EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
            )
            logger.info("Verify OK: Button worked, country code / phone field is displayed.")
        except TimeoutException:
            raise AssertionError("TRANSITION ERROR: After clicking 'Continue with Mobile Number', the phone inputs page did not load!")

    _execute_mobile_number_login(driver, phone, otp)
