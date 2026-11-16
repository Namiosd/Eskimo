import random
import subprocess
import time
import allure
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from config.config import TestConfig
from core.logger import logger
from core.step_tracker import Step
from utils.api_helper import ApiHelper
from pages.base_page import (
    wait_for_element_with_anr_handling,
    handle_notification_onboarding,
    handle_welcome_popup,
)
from pages.profile_page import navigate_to_personal_profile


# ============================================================
# TEST DATA GENERATORS & RESET / TEARDOWN UTILITIES
# ============================================================

def generate_fresh_phone() -> str:
    """
    Generate a fresh 9-digit Vietnam mobile number (after +84) per test run.
    Uses valid VN mobile prefixes (3, 5, 7, 8, 9) + timestamp digits.
    Works with UAT fixed OTP ('1234').
    """
    prefix = random.choice(["3", "5", "7", "8", "9"])
    suffix = f"{int(time.time() * 100) % 100000000:08d}"
    phone = f"{prefix}{suffix}"
    logger.info(f"Generated fresh UAT phone number: +84 {phone}")
    return phone


def generate_fresh_email(prefix: str = "kieu.signup") -> str:
    """
    Generate a fresh unique email address per test run (e.g. kieu.signup+<timestamp>@yopmail.com).
    """
    unique_tag = f"{int(time.time() * 1000)}"
    email = f"{prefix}+{unique_tag}@yopmail.com"
    logger.info(f"Generated fresh UAT email: {email}")
    return email


def dismiss_account_suspended_popup(driver: webdriver.Remote, timeout: int = 5) -> bool:
    """
    Check if the 'Account Suspended' popup (`header` = 'Account Suspended') is displayed,
    and close it via the 'X' button (`img_close`) or 'Cancel' button (`btn_cancel`).
    Returns True if the popup was detected and dismissed.
    """
    try:
        suspended_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/header' and contains(@text, 'Account Suspended')] | "
            "//*[contains(@text, 'Account Suspended') or contains(@text, 'Contact support for assistance')]"
        )
        elems = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((AppiumBy.XPATH, suspended_xpath))
        )
        if elems and elems[0].is_displayed():
            logger.info("Detected 'Account Suspended' popup. Closing popup...")
            close_xpath = (
                "//*[@resource-id='travel.eskimo.esim.uat:id/img_close' or "
                "@resource-id='travel.eskimo.esim.uat:id/btn_cancel' or "
                "@text='Cancel']"
            )
            close_btns = driver.find_elements(AppiumBy.XPATH, close_xpath)
            for btn in close_btns:
                if btn.is_displayed():
                    btn.click()
                    logger.info("✅ Closed 'Account Suspended' popup.")
                    time.sleep(2)
                    return True
    except Exception:
        pass
    return False


def is_on_guest_onboarding(driver: webdriver.Remote, timeout: int = 5) -> bool:
    """
    Check whether the app is currently on the Guest Onboarding screen or Sign Up gate screen.
    Explicitly returns False if the app is on the 'Last step' screen (which also has `et_email`).
    """
    try:
        last_step_elems = driver.find_elements(
            AppiumBy.XPATH,
            "//*[@resource-id='travel.eskimo.esim.uat:id/et_first_name' or @text='Last step' or @text='Complete sign up']"
        )
        if last_step_elems and last_step_elems[0].is_displayed():
            return False
    except Exception:
        pass

    onboarding_xpath = (
        "//*[@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer' or "
        "@resource-id='travel.eskimo.esim.uat:id/txt_claim_offer' or "
        "@text='Claim your offer' or "
        "@resource-id='travel.eskimo.esim.uat:id/btn_signup' or "
        "@resource-id='travel.eskimo.esim.uat:id/lbl_sign_up' or "
        "@resource-id='travel.eskimo.esim.uat:id/txt_login' or "
        "@resource-id='travel.eskimo.esim.uat:id/mobile_number_login' or "
        "@text='Continue with Mobile Number' or "
        "@text='Tiếp tục với số di động']"
    )
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, onboarding_xpath))
        )
        return elem.is_displayed()
    except Exception:
        return False


def auto_logout_if_not_on_onboarding(driver: webdriver.Remote) -> None:
    """
    Check if the app is on the Guest Onboarding screen:
    - If already on Guest Onboarding / Sign Up screen -> do nothing and proceed with the testcase.
    - If stuck on 'Last step' screen -> tap Back and click 'No, I don't want the offer' to exit to Sign Up screen.
    - If logged into Home/Account -> automatically log out via UI
      (Account tab -> Log out -> Confirm Log out), and fallback to resetting app data if needed.
    """
    with allure.step("Check Guest Onboarding state (auto-logout if logged in)"), Step(
        "Check Guest Onboarding state (auto-logout if logged in)"
    ):
        dismiss_account_suspended_popup(driver, timeout=2)

        # If stuck on 'Last step' screen from a previous testcase (e.g. TC_05), exit via retention offer decline
        try:
            last_step_elems = driver.find_elements(
                AppiumBy.XPATH,
                "//*[@resource-id='travel.eskimo.esim.uat:id/et_first_name' or @text='Last step' or @text='Complete sign up']"
            )
            if last_step_elems and last_step_elems[0].is_displayed():
                logger.info("App is currently on 'Last step' screen. Exiting back to Sign Up screen...")
                driver.back()
                time.sleep(2)
                decline_btns = driver.find_elements(
                    AppiumBy.XPATH,
                    "//*[contains(@text, 'want the offer') or "
                    "@resource-id='travel.eskimo.esim.uat:id/txt_no_offer' or "
                    "@resource-id='travel.eskimo.esim.uat:id/btn_no_offer']"
                )
                if decline_btns and decline_btns[0].is_displayed():
                    decline_btns[0].click()
                    time.sleep(2)
        except Exception:
            pass

        if is_on_guest_onboarding(driver, timeout=3):
            logger.info("✅ App is already on Guest Onboarding / Sign Up screen. Proceeding with testcase.")
            return

        handle_notification_onboarding(driver, timeout=3)
        handle_welcome_popup(driver, timeout=3)
        dismiss_account_suspended_popup(driver, timeout=2)

        if is_on_guest_onboarding(driver, timeout=3):
            logger.info("✅ App is already on Guest Onboarding / Sign Up screen. Proceeding with testcase.")
            return

        logger.info("App is NOT on Guest Onboarding screen. Attempting automatic Logout...")

        # Try navigating back up to 3 times if stuck on an inner screen
        for _ in range(3):
            if is_on_guest_onboarding(driver, timeout=2):
                logger.info("✅ Reached Guest Onboarding screen after navigating back.")
                return
            nav_account = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_account")
            if nav_account and nav_account[0].is_displayed():
                break
            handle_welcome_popup(driver, timeout=2)
            dismiss_account_suspended_popup(driver, timeout=2)
            try:
                driver.back()
                time.sleep(2)
            except Exception:
                break

        # Perform UI Logout via Account tab if bottom navigation is accessible
        logged_out_via_ui = False
        try:
            nav_account = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_account")
            if nav_account and nav_account[0].is_displayed():
                nav_account[0].click()
                logger.info("Clicked 'Account' tab to perform automatic logout.")
                time.sleep(2)

                dismiss_account_suspended_popup(driver, timeout=2)

                logout_item_xpath = (
                    "//*[@resource-id='travel.eskimo.esim.uat:id/lbl_logout' or "
                    "@resource-id='travel.eskimo.esim.uat:id/btn_logout' or "
                    "@resource-id='travel.eskimo.esim.uat:id/btn_log_out' or "
                    "@resource-id='travel.eskimo.esim.uat:id/log_out' or "
                    "contains(@text, 'Log out') or contains(@text, 'Log Out')]"
                )
                # Scroll down on Account screen if Log out button is below the fold
                for _ in range(3):
                    logout_btns = driver.find_elements(AppiumBy.XPATH, logout_item_xpath)
                    if logout_btns and logout_btns[0].is_displayed():
                        logout_btns[0].click()
                        logger.info("Clicked 'Log out' option on Account screen.")
                        time.sleep(2)
                        break
                    try:
                        driver.find_element(
                            AppiumBy.ANDROID_UIAUTOMATOR,
                            'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()',
                        )
                        time.sleep(1)
                    except Exception:
                        break

                # Confirm Logout dialog ('Are you sure you want to log out?')
                confirm_logout_xpath = (
                    "//*[@resource-id='travel.eskimo.esim.uat:id/btn_log_out' or "
                    "@resource-id='travel.eskimo.esim.uat:id/btn_logout' or "
                    "@resource-id='travel.eskimo.esim.uat:id/btn_ok' or "
                    "@resource-id='travel.eskimo.esim.uat:id/btn_yes' or "
                    "@text='Log out' or @text='Log Out' or @text='Yes']"
                )
                confirm_btns = driver.find_elements(AppiumBy.XPATH, confirm_logout_xpath)
                if confirm_btns:
                    confirm_btns[-1].click()
                    logger.info("Confirmed 'Log out' on confirmation dialog.")
                    time.sleep(3)
                    logged_out_via_ui = True
        except Exception as e:
            logger.warning(f"UI logout attempt encountered warning: {e}")

        if logged_out_via_ui:
            # Restart PreLoaderActivity after UI logout so Eskimo reloads the Country Code list in memory
            app_package = TestConfig.APP_PACKAGE
            app_activity = TestConfig.APP_ACTIVITY
            device_id = TestConfig.DEVICE_NAME
            try:
                driver.terminate_app(app_package)
            except Exception:
                pass
            try:
                subprocess.run(
                    ["adb", "-s", device_id, "shell", "am", "start", "-W", "-n", f"{app_package}/{app_activity}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=20,
                )
            except Exception:
                pass
            try:
                driver.activate_app(app_package)
            except Exception:
                pass
            time.sleep(4)
            handle_notification_onboarding(driver, timeout=3)
            dismiss_account_suspended_popup(driver, timeout=2)
            if is_on_guest_onboarding(driver, timeout=6):
                logger.info("✅ Successfully logged out via UI and reloaded Guest Onboarding screen.")
                return

        # Fallback: If still not on Guest Onboarding, force clear package data & relaunch
        if not is_on_guest_onboarding(driver, timeout=3):
            logger.info("App still not on Onboarding after UI logout attempt. Forcing clean reset to Guest Onboarding...")
            reset_app_to_guest_onboarding(driver, force_pm_clear=True)


def reset_app_to_guest_onboarding(
    driver: webdriver.Remote,
    rotate_device_id: bool = True,
    force_pm_clear: bool = False,
) -> None:
    """
    Reset application state back to Guest Onboarding screen:
    - Checks for 'Account Suspended' popup, post-signup popups, or logged-in Home/Account screens.
    - Runs `pm clear` if `force_pm_clear=True` or if the app is not on Guest Onboarding.
    - Explicitly starts `PreLoaderActivity` via ADB + `activate_app` so the app never stays stuck on the Android desktop.
    """
    app_package = TestConfig.APP_PACKAGE
    app_activity = TestConfig.APP_ACTIVITY
    device_id = TestConfig.DEVICE_NAME
    with allure.step("Reset app state to Guest Onboarding screen"), Step("Reset app state to Guest Onboarding screen"):
        dismiss_account_suspended_popup(driver, timeout=2)
        handle_welcome_popup(driver, timeout=2)

        need_clear = force_pm_clear
        if not need_clear:
            try:
                logged_in_or_suspended = driver.find_elements(
                    AppiumBy.XPATH,
                    "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home' or "
                    "@resource-id='travel.eskimo.esim.uat:id/navigation_account' or "
                    "@resource-id='travel.eskimo.esim.uat:id/title_in_reward_bonus' or "
                    "contains(@text, 'Account Suspended')]"
                )
                if logged_in_or_suspended or not is_on_guest_onboarding(driver, timeout=3):
                    need_clear = True
            except Exception:
                need_clear = True

        try:
            driver.terminate_app(app_package)
        except Exception:
            pass

        if rotate_device_id:
            try:
                new_android_id = "".join(random.choices("0123456789abcdef", k=16))
                subprocess.run(
                    ["adb", "-s", device_id, "shell", "settings", "put", "secure", "android_id", new_android_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                )
                logger.info(f"Rotated emulator android_id to: {new_android_id}")
            except Exception as e:
                logger.warning(f"Could not rotate android_id: {e}")

        if need_clear:
            try:
                subprocess.run(
                    ["adb", "-s", device_id, "shell", "pm", "clear", app_package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=15,
                )
                logger.info(f"Cleared application data for package '{app_package}'.")
            except Exception as e:
                logger.warning(f"ADB pm clear warning: {e}")

        try:
            subprocess.run(
                ["adb", "-s", device_id, "shell", "am", "start", "-W", "-n", f"{app_package}/{app_activity}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=20,
            )
        except Exception:
            pass

        try:
            driver.activate_app(app_package)
        except Exception:
            pass

        time.sleep(4)
        handle_notification_onboarding(driver)
        dismiss_account_suspended_popup(driver, timeout=3)


def reset_signup_phone_account(
    driver: webdriver.Remote,
    mobile_no: str = TestConfig.SIGNUP_TEST_MOBILE,
    email: str = TestConfig.SIGNUP_TEST_EMAIL,
) -> None:
    """
    Reset the newly registered mobile/email account via Eskimo Stage/UAT API:
      - GET /api/v2.0/Customer/reset-mobile-account?mobileNo=<mobileNo>&countryCode=84
      - GET /api/v2.0/Customer/reset-email-account?email=<email>
    and clear app state back to Guest Onboarding so the same phone/email can be reused.
    """
    with allure.step("Teardown: Reset mobile/email account via API and clear app state"), Step(
        "Teardown: Reset mobile/email account via API and clear app state"
    ):
        api = ApiHelper()
        try:
            if mobile_no:
                api.reset_mobile_account(mobile_no=mobile_no, country_code=TestConfig.COUNTRY_CODE)
            if email:
                api.reset_email_account(email=email)
        except Exception as e:
            logger.warning(f"API account reset warning during teardown: {e}")
        finally:
            reset_app_to_guest_onboarding(driver)


# ============================================================
# NAVIGATION & STEP HELPERS FOR SIGN UP FLOW
# ============================================================

def open_signup_gate_from_onboarding(driver: webdriver.Remote) -> None:
    """
    Ensure the app is on Guest Onboarding (auto-logout if logged in, dismiss 'Account Suspended' if present),
    then click 'Claim your offer' to open the 'Sign up for Eskimo' screen.
    If the app is already on 'Sign up for Eskimo', proceed directly.
    """
    auto_logout_if_not_on_onboarding(driver)

    with allure.step("Navigate to 'Sign up for Eskimo' screen from Onboarding"), Step(
        "Navigate to 'Sign up for Eskimo' screen from Onboarding"
    ):
        gate_or_claim_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_claim_offer' or "
            "@text='Claim your offer' or "
            "@resource-id='travel.eskimo.esim.uat:id/mobile_number_login' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_mobile_number' or "
            "@text='Continue with Mobile Number' or "
            "@text='Tiếp tục với số di động']"
        )
        elem = wait_for_element_with_anr_handling(driver, gate_or_claim_xpath, timeout=60)
        res_id = elem.get_attribute("resource-id") or ""
        text_val = elem.get_attribute("text") or ""

        if "claim_offer" in res_id or text_val == "Claim your offer":
            elem.click()
            logger.info("Clicked 'Claim your offer' to enter Sign Up screen.")
            time.sleep(2)
        else:
            logger.info("Already on 'Sign up for Eskimo' screen.")


def select_continue_with_mobile(driver: webdriver.Remote) -> None:
    """Click 'Continue with Mobile Number' on the 'Sign up for Eskimo' screen."""
    with allure.step("Click 'Continue with Mobile Number'"), Step("Click 'Continue with Mobile Number'"):
        mobile_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/mobile_number_login' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_mobile_number' or "
            "@text='Continue with Mobile Number' or "
            "@text='Tiếp tục với số di động']"
        )
        mobile_btn = wait_for_element_with_anr_handling(driver, mobile_xpath, timeout=30)
        assert mobile_btn.is_displayed() and mobile_btn.is_enabled(), "UI ERROR: 'Continue with Mobile Number' button not active!"
        mobile_btn.click()
        logger.info("Clicked 'Continue with Mobile Number'.")
        time.sleep(2)


def select_continue_with_email(driver: webdriver.Remote) -> None:
    """
    Verify the Email input field (`et_email`) is directly visible on the 'Sign up for Eskimo' screen.
    (On Android Eskimo UAT, the email box and 'Send OTP' button are rendered directly on the Sign Up gate).
    """
    with allure.step("Verify Email input field on 'Sign up for Eskimo' screen"), Step("Verify Email input field on 'Sign up for Eskimo' screen"):
        email_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/et_email' or "
            "@hint='Enter your email']"
        )
        email_field = wait_for_element_with_anr_handling(driver, email_xpath, timeout=30)
        assert email_field.is_displayed(), "UI ERROR: Email input field 'et_email' is not visible on Sign Up screen!"
        logger.info("Verified Email input field is ready on 'Sign up for Eskimo' screen.")


def select_country_code(driver: webdriver.Remote, country_name: str = TestConfig.COUNTRY_SEARCH) -> None:
    """Select country code (+84 Vietnam by default) on the Mobile Number screen."""
    wait = WebDriverWait(driver, 20)
    with allure.step(f"Select country code: {country_name}"), Step(f"Select country code: {country_name}"):
        country_code = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
        )
        current_cc_text = (country_code.text or "").strip()
        if not current_cc_text:
            try:
                inner_tvs = country_code.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
                current_cc_text = " ".join((tv.text or "") for tv in inner_tvs).strip()
            except Exception:
                current_cc_text = ""

        if country_name.lower() == "vietnam" and "84" in current_cc_text:
            logger.info(f"Country code is already set to Vietnam ({current_cc_text}), skipping modal.")
            return
        if country_name.lower() == "singapore" and "65" in current_cc_text:
            logger.info(f"Country code is already set to Singapore ({current_cc_text}), skipping modal.")
            return

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
        search_field.send_keys(country_name)
        time.sleep(1)

        option_xpath = '//android.widget.RelativeLayout[@resource-id="travel.eskimo.esim.uat:id/test"]/android.widget.LinearLayout/android.widget.LinearLayout'
        try:
            country_option = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, option_xpath))
            )
            country_option.click()
            time.sleep(1)
        except TimeoutException:
            logger.warning(
                f"Country list is empty when searching '{country_name}' (post-logout cache issue). "
                "Restarting PreLoaderActivity to reload country list..."
            )
            app_package = TestConfig.APP_PACKAGE
            app_activity = TestConfig.APP_ACTIVITY
            device_id = TestConfig.DEVICE_NAME
            try:
                driver.terminate_app(app_package)
            except Exception:
                pass
            try:
                subprocess.run(
                    ["adb", "-s", device_id, "shell", "am", "start", "-W", "-n", f"{app_package}/{app_activity}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=20,
                )
            except Exception:
                pass
            try:
                driver.activate_app(app_package)
            except Exception:
                pass
            time.sleep(4)
            open_signup_gate_from_onboarding(driver)
            select_continue_with_mobile(driver)

            country_code = wait.until(
                EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
            )
            current_cc_text = (country_code.text or "").strip()
            if country_name.lower() == "vietnam" and "84" in current_cc_text:
                logger.info(f"Country code is already set to Vietnam ({current_cc_text}) after reload.")
                return
            country_code.click()
            time.sleep(1)
            search_field = wait.until(
                EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txtSearch"))
            )
            search_field.clear()
            search_field.send_keys(country_name)
            time.sleep(1)
            country_option = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, option_xpath))
            )
            country_option.click()
            time.sleep(1)


def enter_mobile_and_submit(driver: webdriver.Remote, phone: str, request_otp_channel: bool = True) -> None:
    """Enter mobile phone number, click Continue, and select OTP channel ('WhatsApp') on the bottom sheet."""
    wait = WebDriverWait(driver, 20)
    with allure.step(f"Enter mobile number: {phone}"), Step(f"Enter mobile number: {phone}"):
        phone_field = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
        )
        phone_field.clear()
        phone_field.send_keys(phone)
        logger.info(f"Entered mobile number: {phone}")

        continue_btn = wait.until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//*[@resource-id='travel.eskimo.esim.uat:id/btn_continue' or @resource-id='travel.eskimo.esim.uat:id/txt_continue' or @text='Continue']"
            ))
        )
        if continue_btn.is_enabled():
            continue_btn.click()
            logger.info("Clicked 'Continue' button on Mobile Number screen.")
        else:
            logger.info("'Continue' button is disabled for the entered mobile number.")
        time.sleep(2)

    if request_otp_channel:
        with allure.step("Select OTP delivery channel (WhatsApp / SMS)"), Step("Select OTP delivery channel (WhatsApp / SMS)"):
            channel_xpath = (
                "//*[@resource-id='travel.eskimo.esim.uat:id/cd_whatsapp' or "
                "@resource-id='travel.eskimo.esim.uat:id/btn_whatsapp' or "
                "@resource-id='travel.eskimo.esim.uat:id/cd_sms' or "
                "@resource-id='travel.eskimo.esim.uat:id/btn_sms']"
            )
            try:
                channel_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, channel_xpath))
                )
                channel_btn.click()
                logger.info("Requested OTP via selected channel.")
                time.sleep(2)
            except TimeoutException:
                logger.info("OTP channel bottom sheet did not appear (validation may have blocked prior step).")


def enter_email_and_submit(driver: webdriver.Remote, email: str) -> None:
    """Enter email address into `et_email` on the 'Sign up for Eskimo' screen and click 'Send OTP' (`btn_next`)."""
    wait = WebDriverWait(driver, 20)
    with allure.step(f"Enter sign-up email: {email} and click 'Send OTP'"), Step(f"Enter sign-up email: {email} and click 'Send OTP'"):
        email_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/et_email' or "
            "@hint='Enter your email']"
        )
        email_field = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, email_xpath)))
        email_field.clear()
        email_field.send_keys(email)
        logger.info(f"Entered email: {email}")

        try:
            driver.hide_keyboard()
        except Exception:
            pass

        send_otp_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/btn_next' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_continue' or "
            "@text='Send OTP' or @text='Continue']"
        )
        send_otp_btn = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, send_otp_xpath)))
        if send_otp_btn.is_enabled():
            send_otp_btn.click()
            logger.info("Clicked 'Send OTP' button.")
        time.sleep(3)


def input_otp_code(driver: webdriver.Remote, otp: str = TestConfig.OTP, timeout: int = 35) -> None:
    """Populate the 4-digit OTP code on the Verify OTP screen (default wait timeout: 35s)."""
    wait = WebDriverWait(driver, timeout)
    with allure.step(f"Input OTP code: {otp} (wait up to {timeout}s)"), Step(f"Input OTP code: {otp} (wait up to {timeout}s)"):
        time.sleep(4)
        wait.until(EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/otp1")))
        for i, digit in enumerate(otp, start=1):
            otp_field = driver.find_element(AppiumBy.ID, f"travel.eskimo.esim.uat:id/otp{i}")
            otp_field.clear()
            otp_field.send_keys(digit)
        logger.info(f"Submitted OTP code: {otp}")
        time.sleep(3)


def verify_on_last_step_screen(driver: webdriver.Remote) -> None:
    """Verify that the 'Last step' (Create Account info) screen is displayed."""
    with allure.step("Verify 'Last step' account info screen is displayed"), Step("Verify 'Last step' account info screen is displayed"):
        last_step_xpath = (
            "//*[@text='Last step' or "
            "@text='Complete sign up' or "
            "@resource-id='travel.eskimo.esim.uat:id/et_first_name']"
        )
        elem = wait_for_element_with_anr_handling(driver, last_step_xpath, timeout=30)
        assert elem.is_displayed(), "TRANSITION ERROR: Did not reach 'Last step' screen after OTP verification!"
        logger.info("Verified 'Last step' screen is loaded.")


def fill_last_step_account_info(
    driver: webdriver.Remote,
    first_name: str = "Kieu",
    last_name: str = "Nguyen",
    email: str = None,
    referral_code: str = None,
    submit: bool = True,
) -> None:
    """
    Fill 'First name', 'Last name', 'Email' (if visible), and optional 'Referral/gift code'
    on the 'Last step' screen, then optionally click 'Complete sign up'.
    """
    verify_on_last_step_screen(driver)

    if email is None:
        email = generate_fresh_email()

    with allure.step(f"Fill account info (First: {first_name}, Last: {last_name}, Email: {email})"), Step(f"Fill account info (First: {first_name}, Last: {last_name}, Email: {email})"):
        # 1. First name
        fn_field = driver.find_element(
            AppiumBy.XPATH,
            "//*[@resource-id='travel.eskimo.esim.uat:id/et_first_name'] | (//android.widget.EditText)[1]"
        )
        fn_field.clear()
        fn_field.send_keys(first_name)

        # 2. Last name
        ln_field = driver.find_element(
            AppiumBy.XPATH,
            "//*[@resource-id='travel.eskimo.esim.uat:id/et_last_name'] | (//android.widget.EditText)[2]"
        )
        ln_field.clear()
        ln_field.send_keys(last_name)

        # 3. Email field (present when signing up via Mobile Number)
        try:
            email_fields = driver.find_elements(
                AppiumBy.XPATH,
                "//*[@resource-id='travel.eskimo.esim.uat:id/et_email' or "
                "@resource-id='travel.eskimo.esim.uat:id/et_billing_email' or "
                "contains(@hint, 'eskimo.travel')] | (//android.widget.EditText)[3]"
            )
            if email_fields and email_fields[0].is_displayed():
                hint_or_text = (email_fields[0].get_attribute("hint") or "").lower()
                if "referral" not in hint_or_text:
                    email_fields[0].clear()
                    email_fields[0].send_keys(email)
        except Exception as e:
            logger.info(f"Optional 3rd field (Email) skip/info: {e}")

        try:
            driver.hide_keyboard()
        except Exception:
            pass

    # 4. Optional Referral/gift code
    if referral_code is not None:
        apply_referral_code_on_last_step(driver, referral_code)

    # 5. Click 'Complete sign up'
    if submit:
        click_complete_sign_up(driver)


def apply_referral_code_on_last_step(driver: webdriver.Remote, referral_code: str) -> None:
    """Enter a referral/gift code on the 'Last step' screen and click 'Apply'."""
    with allure.step(f"Apply referral/gift code: {referral_code}"), Step(f"Apply referral/gift code: {referral_code}"):
        change_btns = driver.find_elements(
            AppiumBy.XPATH,
            "//*[@text='Change' or @resource-id='travel.eskimo.esim.uat:id/txt_change' or @resource-id='travel.eskimo.esim.uat:id/btn_change']"
        )
        if change_btns and change_btns[0].is_displayed():
            change_btns[0].click()
            time.sleep(1)

        ref_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/et_referral_code' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_promo_code' or "
            "contains(@hint, 'referral code') or contains(@text, 'referral code')] | "
            "(//android.widget.EditText)[last()]"
        )
        ref_field = wait_for_element_with_anr_handling(driver, ref_xpath, timeout=15)
        ref_field.clear()
        ref_field.send_keys(referral_code)
        logger.info(f"Entered referral/gift code: {referral_code}")

        try:
            driver.hide_keyboard()
        except Exception:
            pass

        apply_xpath = (
            "//*[@text='Apply' or "
            "@resource-id='travel.eskimo.esim.uat:id/btn_apply' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_apply_code']"
        )
        apply_btn = wait_for_element_with_anr_handling(driver, apply_xpath, timeout=15)
        apply_btn.click()
        logger.info("Clicked 'Apply' for referral/gift code.")
        time.sleep(2)


def is_complete_sign_up_enabled(driver: webdriver.Remote) -> bool:
    """
    Check whether the 'Complete sign up' button on 'Last step' is ready/enabled:
    On Android Eskimo UAT, the CardView `btn_continue` keeps XML `enabled='true'` even when greyed out,
    so we check both the button presence and whether all required fields (`et_first_name`, `et_last_name`, `et_email`)
    are filled (non-empty and `showing-hint != 'true'`).
    """
    btn_xpath = (
        "//*[@text='Complete sign up' or "
        "@resource-id='travel.eskimo.esim.uat:id/btn_complete_sign_up' or "
        "@resource-id='travel.eskimo.esim.uat:id/txt_complete_sign_up' or "
        "@resource-id='travel.eskimo.esim.uat:id/btn_continue']"
    )
    elem = wait_for_element_with_anr_handling(driver, btn_xpath, timeout=15)
    enabled_attr = (elem.get_attribute("enabled") or "").lower() == "true"
    if not enabled_attr:
        return False

    try:
        fn_elem = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_first_name")
        ln_elem = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_last_name")
        fn_text = (fn_elem.text or "").strip()
        ln_text = (ln_elem.text or "").strip()
        fn_ok = len(fn_text) > 0 and fn_text.lower() != "first name"
        ln_ok = len(ln_text) > 0 and ln_text.lower() != "last name"

        email_elems = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_email")
        if email_elems and email_elems[0].is_displayed():
            em_text = (email_elems[0].text or "").strip()
            em_ok = len(em_text) > 0 and em_text.lower() != "mo@eskimo.travel"
        else:
            em_ok = True

        return fn_ok and ln_ok and em_ok
    except Exception as e:
        logger.warning(f"is_complete_sign_up_enabled check warning: {e}")
        return False


def click_complete_sign_up(driver: webdriver.Remote) -> None:
    """Click the 'Complete sign up' CTA button on the 'Last step' screen."""
    with allure.step("Click 'Complete sign up' button"), Step("Click 'Complete sign up' button"):
        btn_xpath = (
            "//*[@text='Complete sign up' or "
            "@resource-id='travel.eskimo.esim.uat:id/btn_complete_sign_up' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_complete_sign_up' or "
            "@resource-id='travel.eskimo.esim.uat:id/btn_continue']"
        )
        complete_btn = wait_for_element_with_anr_handling(driver, btn_xpath, timeout=20)
        assert complete_btn.is_displayed(), "UI ERROR: 'Complete sign up' button is not visible!"
        complete_btn.click()
        logger.info("Clicked 'Complete sign up'.")
        time.sleep(3)


def verify_home_screen_after_signup(driver: webdriver.Remote, check_signup_offer: bool = False) -> bool:
    """
    Dismiss post-signup notification/welcome overlays (including the 'Get 35% off your first purchase'
    popup by clicking its top-right 'X' button `img_close`) and verify user lands on the Home screen.
    Note: The 'Buy now, travel anytime!' CTA (`btn_invite`) is reserved for the Buy Data Plan task.
    """
    offer_detected = False
    with allure.step("Dismiss post-signup popups (click 'X' on 35% off popup) and verify Home screen"), Step(
        "Dismiss post-signup popups (click 'X' on 35% off popup) and verify Home screen"
    ):
        end_time = time.monotonic() + 60
        home_tab = None

        while time.monotonic() < end_time:
            # 1. If Notification Onboarding ('Allow notifications' / 'Skip') is shown, dismiss it
            try:
                notif_btns = driver.find_elements(
                    AppiumBy.XPATH,
                    "//*[@resource-id='travel.eskimo.esim.uat:id/btn_allow' or @resource-id='travel.eskimo.esim.uat:id/btn_skip']",
                )
                if notif_btns and notif_btns[0].is_displayed():
                    handle_notification_onboarding(driver, timeout=3)
                    continue
            except Exception:
                pass

            # 2. If 'Get 35% off your first purchase' (or Welcome) popup is shown, click 'X' (`img_close`)
            try:
                popup_elems = driver.find_elements(
                    AppiumBy.XPATH,
                    "//*[@resource-id='travel.eskimo.esim.uat:id/title_in_reward_bonus' or "
                    "contains(@text, 'Get 35% off') or "
                    "contains(@text, 'first purchase') or "
                    "contains(@text, 'Buy now, travel anytime') or "
                    "contains(@text, 'Welcome')]",
                )
                if popup_elems and popup_elems[0].is_displayed():
                    offer_detected = True
                    logger.info(f"Detected post-signup popup: '{popup_elems[0].text}'. Clicking 'X' (`img_close`) to go to Home...")
                    if handle_welcome_popup(driver, timeout=3):
                        continue
            except Exception:
                pass

            # 3. Check if Home screen navigation bar is now visible
            try:
                home_elems = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home")
                if home_elems and home_elems[0].is_displayed():
                    # Wait briefly in case the 35% off popup animates in right after Home loads
                    time.sleep(2)
                    if handle_welcome_popup(driver, timeout=3):
                        offer_detected = True
                    home_tab = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home")
                    if home_tab.is_displayed():
                        break
            except Exception:
                pass

            time.sleep(2)

        assert home_tab is not None and home_tab.is_displayed(), (
            "Home screen navigation bar was not displayed after Sign Up!"
        )
        logger.info("✅ Sign Up complete! Closed post-signup popup via 'X' and verified Home screen.")

        if check_signup_offer:
            logger.info(f"Sign-up offer visibility check result: {offer_detected}")
        return offer_detected


# ============================================================
# BACK BUTTON ON 'LAST STEP' -> RETENTION OFFER FLOW
# ("Your free data is waiting" -> Claim my offer vs No, I don't want the offer)
# ============================================================

def tap_back_on_last_step(driver: webdriver.Remote) -> None:
    """
    Tap the top-left Back arrow ('<-') on the 'Last step' screen and verify
    the retention screen ('Your free data is waiting') appears.
    """
    with allure.step("Tap Back button on 'Last step' screen"), Step("Tap Back button on 'Last step' screen"):
        back_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/btn_back' or "
            "@resource-id='travel.eskimo.esim.uat:id/back' or "
            "@resource-id='travel.eskimo.esim.uat:id/img_back' or "
            "@content-desc='Navigate up']"
        )
        back_elems = driver.find_elements(AppiumBy.XPATH, back_xpath)
        if back_elems and back_elems[0].is_displayed():
            back_elems[0].click()
        else:
            driver.back()
        time.sleep(2)

    with allure.step("Verify retention screen 'Your free data is waiting' is shown"), Step("Verify retention screen 'Your free data is waiting' is shown"):
        retention_xpath = (
            "//*[contains(@text, 'Your free data is waiting') or "
            "contains(@text, 'Complete sign up to claim it') or "
            "contains(@text, 'Free 250 MB Global eSIM')]"
        )
        retention_header = wait_for_element_with_anr_handling(driver, retention_xpath, timeout=20)
        assert retention_header.is_displayed(), "Retention offer screen ('Your free data is waiting') did not appear after pressing Back on Last step!"
        logger.info("Verified retention offer screen 'Your free data is waiting' is displayed.")


def handle_last_step_retention_offer(driver: webdriver.Remote, claim_offer: bool = True) -> None:
    """
    Handle the 'Your free data is waiting' retention screen:
    - Branch 1 (claim_offer=True): Click 'Claim my offer' -> Verify return to 'Last step'
      with 'FREE250MB' ('Applied') pre-filled and 'Change' option visible.
    - Branch 2 (claim_offer=False): Click 'No, I don't want the offer' -> Verify exit
      back to the Sign Up screen and user is NOT logged into Home.
    """
    if claim_offer:
        with allure.step("Branch 1: Click 'Claim my offer' on retention screen"), Step("Branch 1: Click 'Claim my offer' on retention screen"):
            claim_xpath = (
                "//*[@text='Claim my offer' or "
                "@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer' or "
                "@resource-id='travel.eskimo.esim.uat:id/txt_claim_offer']"
            )
            claim_btn = wait_for_element_with_anr_handling(driver, claim_xpath, timeout=15)
            claim_btn.click()
            logger.info("Clicked 'Claim my offer' on retention screen.")
            time.sleep(2)

        with allure.step("Verify returned to 'Last step' with 'FREE250MB' (Applied) pre-filled"), Step("Verify returned to 'Last step' with 'FREE250MB' (Applied) pre-filled"):
            verify_on_last_step_screen(driver)
            applied_xpath = (
                "//*[contains(@text, 'FREE250MB') or contains(@text, 'Applied') or @text='Change']"
            )
            applied_badge = wait_for_element_with_anr_handling(driver, applied_xpath, timeout=15)
            assert applied_badge.is_displayed(), "Expected 'FREE250MB' (Applied) voucher card to be pre-filled on 'Last step'!"
            logger.info("Verified 'FREE250MB' (✓ Applied) is automatically pre-filled on 'Last step'.")
    else:
        with allure.step("Branch 2: Click 'No, I don't want the offer' to abandon Last step"), Step("Branch 2: Click 'No, I don't want the offer' to abandon Last step"):
            decline_xpath = (
                "//*[contains(@text, 'want the offer') or "
                "@resource-id='travel.eskimo.esim.uat:id/txt_no_offer' or "
                "@resource-id='travel.eskimo.esim.uat:id/btn_no_offer']"
            )
            decline_btn = wait_for_element_with_anr_handling(driver, decline_xpath, timeout=15)
            decline_btn.click()
            logger.info("Clicked 'No, I don't want the offer'.")
            time.sleep(2)

        with allure.step("Verify exited 'Last step' back to Sign Up screen (not on Home)"), Step("Verify exited 'Last step' back to Sign Up screen (not on Home)"):
            signup_gate_xpath = (
                "//*[@text='Continue with Mobile Number' or "
                "@resource-id='travel.eskimo.esim.uat:id/et_email' or "
                "@resource-id='travel.eskimo.esim.uat:id/lbl_sign_up' or "
                "@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer']"
            )
            gate_elem = wait_for_element_with_anr_handling(driver, signup_gate_xpath, timeout=20)
            assert gate_elem.is_displayed(), "Expected to return to Sign Up screen after declining retention offer!"
            home_elems = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home")
            assert len(home_elems) == 0, "SECURITY/FLOW ERROR: User should NOT be logged into Home after declining sign-up completion!"
            logger.info("Verified user returned to Sign Up screen and is not logged in.")


def verify_already_registered_email_popup(driver: webdriver.Remote) -> None:
    """
    Verify the bottom-sheet 'This email is already in use' appears after clicking 'Send OTP'
    with an already registered email (e.g. ahko355@yopmail.com), and dismiss it via
    'Sign up with a different email'.
    """
    with allure.step("Verify 'This email is already in use' popup is displayed"), Step(
        "Verify 'This email is already in use' popup is displayed"
    ):
        # Wait up to 30s for any active loading spinner (`progress_nearby`) to disappear
        end_wait = time.monotonic() + 30
        while time.monotonic() < end_wait:
            try:
                spinners = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/progress_nearby")
                if not spinners or not spinners[0].is_displayed():
                    break
            except Exception:
                break
            time.sleep(1)

        popup_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/design_bottom_sheet' or "
            "contains(@text, 'This email is already in use') or "
            "contains(@text, 'This email is linked to an existing') or "
            "contains(@text, 'đã được sử dụng') or "
            "contains(@text, 'đã liên kết') or "
            "@text='Log in with mobile number' or "
            "@text='Sign up with a different email']"
        )
        popup_elem = wait_for_element_with_anr_handling(driver, popup_xpath, timeout=25)
        assert popup_elem.is_displayed(), (
            "VALIDATION ERROR: Expected 'This email is already in use' bottom-sheet did not appear!"
        )
        logger.info("Verified 'This email is already in use' popup is displayed.")

        # Verify action buttons on the popup
        diff_email_btns = driver.find_elements(
            AppiumBy.XPATH,
            "//*[@text='Sign up with a different email' or contains(@text, 'different email') or contains(@text, 'email khác') or @resource-id='travel.eskimo.esim.uat:id/btn_cancel']"
        )
        if diff_email_btns and diff_email_btns[0].is_displayed():
            diff_email_btns[0].click()
            logger.info("Clicked 'Sign up with a different email' to dismiss popup.")
            time.sleep(1)


def verify_error_shown_and_not_progressed(driver: webdriver.Remote, stay_Element_xpath: str) -> None:
    """
    Verify that an error message/dialog/bottom-sheet is shown (or screen stays on current step)
    for negative validation test cases.
    Waits for any active loading spinner (`progress_nearby`) to disappear first.
    """
    with allure.step("Verify error state / cannot continue to next step"), Step("Verify error state / cannot continue to next step"):
        # Wait up to 30s for the loading dialog (`progress_nearby`) to disappear
        end_wait = time.monotonic() + 30
        while time.monotonic() < end_wait:
            try:
                spinners = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/progress_nearby")
                if not spinners or not spinners[0].is_displayed():
                    break
            except Exception:
                break
            time.sleep(1)
        time.sleep(1)

        error_xpath = (
            "//*[@resource-id='travel.eskimo.esim.uat:id/oops_image' or "
            "@resource-id='travel.eskimo.esim.uat:id/design_bottom_sheet' or "
            "@resource-id='travel.eskimo.esim.uat:id/txt_error' or "
            "@resource-id='travel.eskimo.esim.uat:id/tv_error' or "
            "@resource-id='travel.eskimo.esim.uat:id/textinput_error' or "
            "contains(@text, 'invalid') or contains(@text, 'Invalid') or "
            "contains(@text, 'already') or contains(@text, 'registered') or "
            "contains(@text, 'linked') or contains(@text, 'exist') or "
            "contains(@text, 'wrong') or contains(@text, 'error') or "
            "contains(@text, 'Error') or contains(@text, 'Sorry')]"
        )
        error_elems = driver.find_elements(AppiumBy.XPATH, error_xpath)
        stay_elems = driver.find_elements(AppiumBy.XPATH, stay_Element_xpath)

        assert len(error_elems) > 0 or len(stay_elems) > 0, (
            f"Expected error indicator or to stay on '{stay_Element_xpath}', but neither was found!"
        )
        logger.info("Verified error message or blocked progression as expected.")

        # Dismiss error modal if 'Okay' / 'OK' / close button is present
        close_btns = driver.find_elements(
            AppiumBy.XPATH,
            "//*[@resource-id='travel.eskimo.esim.uat:id/img_close' or @resource-id='travel.eskimo.esim.uat:id/btn_ok' or @text='Okay' or @text='OK']"
        )
        if close_btns and close_btns[0].is_displayed():
            close_btns[0].click()
            time.sleep(1)
