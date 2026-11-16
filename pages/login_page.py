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
    """
    Perform mobile number input, OTP verification, and post-login resolution stages.
    Pattern: Check UI -> Action -> Verify
    """
    wait = WebDriverWait(driver, 20)

    # ============================================================
    # BƯỚC 3: Chọn mã vùng Quốc gia (+84 Vietnam)
    # ============================================================
    with allure.step("[Check UI] Verify Country Code selector is visible"), Step("[Check UI] Verify Country Code selector is visible"):
        country_code = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
        )
        assert country_code.is_displayed(), "UI ERROR: Country code selector is not visible!"
        logger.info("✅ [Check UI] Country code selector is visible.")

    with allure.step("[Action] Select Vietnam country code (+84)"), Step("[Action] Select Vietnam country code (+84)"):
        current_cc_text = (country_code.text or "").strip()
        if not current_cc_text:
            try:
                inner_tvs = country_code.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
                current_cc_text = " ".join((tv.text or "") for tv in inner_tvs).strip()
            except Exception:
                current_cc_text = ""

        if "84" in current_cc_text:
            logger.info(f"✅ [Action] Country code is already set to Vietnam ({current_cc_text}), skipping modal.")
        else:
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
            search_field.clear()
            search_field.send_keys(TestConfig.COUNTRY_SEARCH)
            time.sleep(1)

            vietnam_option = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH,
                    '//android.widget.RelativeLayout[@resource-id="travel.eskimo.esim.uat:id/test"]/android.widget.LinearLayout/android.widget.LinearLayout'))
            )
            vietnam_option.click()
            logger.info("✅ [Action] Selected Vietnam (+84) from Country Code list.")

    with allure.step("[Verify] Verify return to Mobile Number input screen with Country Code ready"), Step("[Verify] Verify return to Mobile Number input screen with Country Code ready"):
        phone_field = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
        )
        assert phone_field.is_displayed(), "TRANSITION ERROR: Phone number input field is not visible after country selection!"
        logger.info("✅ [Verify] Country code ready and phone number input field is displayed.")

    # ============================================================
    # BƯỚC 4: Nhập số điện thoại & Click Continue
    # ============================================================
    with allure.step("[Check UI] Verify phone number input field is visible and enabled"), Step("[Check UI] Verify phone number input field is visible and enabled"):
        phone_field = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
        )
        assert phone_field.is_displayed() and phone_field.is_enabled(), "UI ERROR: Phone number field is not visible or disabled!"
        logger.info("✅ [Check UI] Phone number input field is visible and enabled.")

    with allure.step(f"[Action] Enter phone number ({phone}) and click 'Continue'"), Step(f"[Action] Enter phone number ({phone}) and click 'Continue'"):
        phone_field.clear()
        phone_field.send_keys(phone)
        logger.info(f"✅ [Action] Entered phone number: {phone}")

        continue_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_continue"))
        )
        assert continue_btn.is_displayed() and continue_btn.is_enabled(), "UI ERROR: 'Continue' button is not active after entering phone number!"
        continue_btn.click()
        logger.info("✅ [Action] Clicked 'Continue' button.")

    with allure.step("[Verify] Verify OTP delivery channel bottom sheet is displayed"), Step("[Verify] Verify OTP delivery channel bottom sheet is displayed"):
        try:
            whatsapp_btn = wait.until(
                EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_whatsapp"))
            )
            assert whatsapp_btn.is_displayed(), "TRANSITION ERROR: OTP channel bottom sheet did not appear!"
            logger.info("✅ [Verify] OTP delivery channel bottom sheet is displayed.")
        except TimeoutException:
            raise AssertionError("TRANSITION ERROR: After clicking 'Continue', OTP channel bottom sheet did not load!")

    # ============================================================
    # BƯỚC 5: Chọn kênh nhận OTP qua WhatsApp
    # ============================================================
    with allure.step("[Check UI] Verify 'WhatsApp' button on OTP bottom sheet is visible and active"), Step("[Check UI] Verify 'WhatsApp' button on OTP bottom sheet is visible and active"):
        whatsapp_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_whatsapp"))
        )
        assert whatsapp_btn.is_displayed() and whatsapp_btn.is_enabled(), "UI ERROR: 'WhatsApp' OTP button is not active!"
        logger.info("✅ [Check UI] 'WhatsApp' OTP button is visible and active.")

    with allure.step("[Action] Click 'WhatsApp' button to request OTP"), Step("[Action] Click 'WhatsApp' button to request OTP"):
        whatsapp_btn.click()
        logger.info("✅ [Action] Clicked 'WhatsApp' to request OTP.")

    with allure.step("[Verify] Verify transition to OTP input screen"), Step("[Verify] Verify transition to OTP input screen"):
        time.sleep(6)
        try:
            otp_field_1 = wait.until(
                EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/otp1"))
            )
            assert otp_field_1.is_displayed(), "TRANSITION ERROR: OTP input screen is not displayed!"
            logger.info("✅ [Verify] Transitioned to OTP input screen successfully.")
        except TimeoutException:
            raise AssertionError("TRANSITION ERROR: After clicking 'WhatsApp', OTP screen did not appear!")

    # ============================================================
    # BƯỚC 6: Nhập mã OTP & Xác nhận vào màn hình Home
    # ============================================================
    with allure.step("[Check UI] Verify all 4 OTP input boxes (otp1..otp4) are visible"), Step("[Check UI] Verify all 4 OTP input boxes (otp1..otp4) are visible"):
        for i in range(1, 5):
            otp_box = wait.until(
                EC.presence_of_element_located((AppiumBy.ID, f"travel.eskimo.esim.uat:id/otp{i}"))
            )
            assert otp_box.is_displayed(), f"UI ERROR: OTP box {i} is not visible!"
        logger.info("✅ [Check UI] All 4 OTP input boxes (otp1..otp4) are displayed.")

    with allure.step(f"[Action] Input 4-digit OTP code: {otp}"), Step(f"[Action] Input 4-digit OTP code: {otp}"):
        for i, digit in enumerate(otp, start=1):
            otp_field = driver.find_element(AppiumBy.ID, f"travel.eskimo.esim.uat:id/otp{i}")
            otp_field.send_keys(digit)
        logger.info(f"✅ [Action] Submitted OTP code: {otp}")

    with allure.step("[Verify] Dismiss onboarding popups and verify Home screen is loaded"), Step("[Verify] Dismiss onboarding popups and verify Home screen is loaded"):
        handle_notification_onboarding(driver)
        handle_welcome_popup(driver)

        time.sleep(2)
        home_tab = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home']", timeout=60)
        assert home_tab.is_displayed(), "TRANSITION ERROR: Home screen navigation tab not visible after submitting OTP!"
        logger.info("✅ [Verify] Authentication complete! Home screen dashboard is fully loaded.")


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
            
        elif resource_id in [
            "travel.eskimo.esim.uat:id/txt_login",
            "travel.eskimo.esim.uat:id/cd_login",
            "travel.eskimo.esim.uat:id/tv_explore_plans",
            "travel.eskimo.esim.uat:id/btn_claim_offer",
        ]:
            # ============================================================
            # BƯỚC 1: Nút Log in trên màn hình Onboarding
            # ============================================================
            with allure.step("[Check UI] Verify 'Log in' button is visible and active on Onboarding screen"), Step("[Check UI] Verify 'Log in' button is visible and active on Onboarding screen"):
                login_btn = wait.until(
                    EC.element_to_be_clickable((
                        AppiumBy.XPATH,
                        "//*[@resource-id='travel.eskimo.esim.uat:id/cd_login' or @resource-id='travel.eskimo.esim.uat:id/txt_login']"
                    ))
                )
                assert login_btn.is_displayed() and login_btn.is_enabled(), "UI ERROR: 'Log in' button is not visible or disabled!"
                logger.info("✅ [Check UI] 'Log in' button is visible and active.")

            with allure.step("[Action] Click 'Log in' button"), Step("[Action] Click 'Log in' button"):
                login_btn.click()
                logger.info("✅ [Action] Clicked 'Log in' button.")
                time.sleep(2)

            with allure.step("[Verify] Verify transition to 'Welcome back' login screen"), Step("[Verify] Verify transition to 'Welcome back' login screen"):
                welcome_el = wait_for_element_with_anr_handling(
                    driver,
                    "//android.widget.TextView[@text='Welcome back'] | //*[@text='Continue with Mobile Number']",
                    timeout=30,
                )
                assert welcome_el.is_displayed(), "TRANSITION ERROR: 'Welcome back' screen did not appear after clicking 'Log in'!"
                logger.info("✅ [Verify] 'Welcome back' screen is displayed.")
            
        else:
            logger.info("Directly on Sign up or Welcome back gate.")
            
    except Exception as e:
        raise Exception(f"Unable to recognize target login gate screen layout state: {e}")

    # ============================================================
    # BƯỚC 2: Chọn 'Continue with Mobile Number'
    # ============================================================
    with allure.step("[Check UI] Verify 'Continue with Mobile Number' button is visible and active"), Step("[Check UI] Verify 'Continue with Mobile Number' button is visible and active"):
        mobile_btn = wait_for_element_with_anr_handling(driver, "//*[@text='Continue with Mobile Number']", timeout=60)
        assert mobile_btn.is_displayed(), "UI ERROR: 'Continue with Mobile Number' button is not visible on login screen!"
        assert mobile_btn.is_enabled(), "UI ERROR: 'Continue with Mobile Number' button is disabled!"
        logger.info("✅ [Check UI] 'Continue with Mobile Number' button is displayed and active.")

    with allure.step("[Action] Click 'Continue with Mobile Number' button"), Step("[Action] Click 'Continue with Mobile Number' button"):
        mobile_btn.click()
        logger.info("✅ [Action] Clicked 'Continue with Mobile Number' button.")
    
    with allure.step("[Verify] Verify transition to Mobile Number input screen"), Step("[Verify] Verify transition to Mobile Number input screen"):
        try:
            wait.until(
                EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
            )
            logger.info("✅ [Verify] Button worked, country code / phone field is displayed.")
        except TimeoutException:
            raise AssertionError("TRANSITION ERROR: After clicking 'Continue with Mobile Number', the phone inputs page did not load!")

    _execute_mobile_number_login(driver, phone, otp)
