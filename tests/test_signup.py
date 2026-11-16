import os
import sys
import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy

# Ensure ESKIMO project root is in sys.path regardless of working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import TestConfig
from core.logger import logger
from utils.api_helper import ApiHelper
from pages.signup_page import (
    generate_fresh_phone,
    generate_fresh_email,
    dismiss_account_suspended_popup,
    auto_logout_if_not_on_onboarding,
    reset_app_to_guest_onboarding,
    reset_signup_phone_account,
    open_signup_gate_from_onboarding,
    select_continue_with_mobile,
    select_continue_with_email,
    select_country_code,
    enter_mobile_and_submit,
    enter_email_and_submit,
    input_otp_code,
    verify_on_last_step_screen,
    fill_last_step_account_info,
    apply_referral_code_on_last_step,
    is_complete_sign_up_enabled,
    verify_home_screen_after_signup,
    tap_back_on_last_step,
    handle_last_step_retention_offer,
    verify_already_registered_email_popup,
    verify_error_shown_and_not_progressed,
)


TEST_MOBILE = TestConfig.SIGNUP_TEST_MOBILE  # "372217263"
Test_mobile = TEST_MOBILE
TEST_EMAIL = TestConfig.SIGNUP_TEST_EMAIL    # "kieu.signup.auto@yopmail.com"
VALID_REFERRAL_CODE = "KIEU1606"
INVALID_REFERRAL_CODE = "INVALID9999"
REGISTERED_EMAIL = TestConfig.REGISTERED_EMAIL  # "ahko355@yopmail.com"
REGISTERED_PHONE = TestConfig.REGISTERED_PHONE  # "372217315"
REGISTERED_PHONE_COUNTRY = TestConfig.REGISTERED_PHONE_COUNTRY  # "Singapore" (+65)


@pytest.fixture(scope="function")
def clean_signup_driver(driver):
    """
    Before each Sign Up test:
      1. Check if app is on Guest Onboarding; if not, automatically logout (and close 'Account Suspended' popup if present).
      2. Call Eskimo Stage API to reset TEST_MOBILE (372217263) and TEST_EMAIL.
      3. Ensure the app is on a clean Guest Onboarding state.
    After each test:
      - Ensure app returns to Guest Onboarding (keeping the registered account in backend
        if needed by the immediately following already-registered test).
    """
    dismiss_account_suspended_popup(driver, timeout=3)
    auto_logout_if_not_on_onboarding(driver)
    api = ApiHelper()
    api.reset_mobile_account(TEST_MOBILE)
    api.reset_email_account(TEST_EMAIL)
    dismiss_account_suspended_popup(driver, timeout=3)
    yield driver
    auto_logout_if_not_on_onboarding(driver)


# ============================================================
# 1. VALIDATION & NEGATIVE FLOWS FIRST (Do not complete sign-up)
# ============================================================

@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_01: Invalid Email format -> Error shown, cannot continue")
@allure.severity(allure.severity_level.NORMAL)
def test_signup_01_invalid_email_format(clean_signup_driver) -> None:
    """
    TC_SIGNUP_01 (AC3 - Email format validation):
    Enter invalid email format -> Click Send OTP -> Verify error shown or progression blocked.
    """
    logger.info("Executing TC_SIGNUP_01: Invalid email format validation...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_email(clean_signup_driver)
    enter_email_and_submit(clean_signup_driver, "invalid-email-format@")

    otp_fields = clean_signup_driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/otp1")
    assert len(otp_fields) == 0, "VALIDATION ERROR: App navigated to OTP screen with an invalid email!"
    verify_error_shown_and_not_progressed(
        clean_signup_driver,
        stay_Element_xpath="//*[@resource-id='travel.eskimo.esim.uat:id/et_email']"
    )
    logger.info("TC_SIGNUP_01 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_02: Already registered Email -> 'This email is already in use' popup shown")
@allure.severity(allure.severity_level.NORMAL)
def test_signup_02_already_registered_email(clean_signup_driver) -> None:
    """
    TC_SIGNUP_02 (AC5 - Already registered Email):
    Enter 'ahko355@yopmail.com' -> Click Send OTP -> Verify 'This email is already in use'
    bottom-sheet appears ('Log in with mobile number' / 'Sign up with a different email')
    and user is not logged in.
    """
    logger.info("Executing TC_SIGNUP_02: Already registered email...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_email(clean_signup_driver)
    enter_email_and_submit(clean_signup_driver, REGISTERED_EMAIL)

    verify_already_registered_email_popup(clean_signup_driver)
    home_elems = clean_signup_driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home")
    assert len(home_elems) == 0, "ERROR: User should not be logged in with already registered email on Sign Up!"
    logger.info("TC_SIGNUP_02 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_03: Invalid Phone Number format (whitespace) -> Cannot continue")
@allure.severity(allure.severity_level.NORMAL)
# @pytest.mark.skip(reason="Tạm khóa vì API Stage chưa chặn format số điện thoại ngắn")
def test_signup_03_invalid_phone_format(clean_signup_driver) -> None:
    """
    TC_SIGNUP_03 (AC3 - Phone format validation):
    Enter whitespace ('   ') into mobile number field -> Verify Continue is blocked
    and app stays on Mobile Number screen without reaching OTP screen.
    """
    logger.info("Executing TC_SIGNUP_03: Invalid phone format (whitespace) validation...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, "   ", request_otp_channel=False)

    otp_fields = clean_signup_driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/otp1")
    assert len(otp_fields) == 0, "VALIDATION ERROR: App navigated to OTP screen with whitespace phone number!"
    verify_error_shown_and_not_progressed(
        clean_signup_driver,
        stay_Element_xpath="//*[@resource-id='travel.eskimo.esim.uat:id/et_mobile_number']"
    )
    logger.info("TC_SIGNUP_03 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_04: Wrong OTP code -> Error shown, stays on OTP screen")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_04_wrong_otp(clean_signup_driver) -> None:
    """
    TC_SIGNUP_04 (AC4 - Wrong OTP):
    Enter TEST_MOBILE (reset before test) -> Input wrong OTP ('0000') -> Verify error shown and stays on OTP screen.
    """
    logger.info("Executing TC_SIGNUP_04: Wrong OTP verification...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, "0000")

    verify_error_shown_and_not_progressed(
        clean_signup_driver,
        stay_Element_xpath="//*[@resource-id='travel.eskimo.esim.uat:id/otp1']"
    )
    last_step_elems = clean_signup_driver.find_elements(AppiumBy.XPATH, "//*[@text='Last step']")
    assert len(last_step_elems) == 0, "SECURITY ERROR: Reached 'Last step' despite entering wrong OTP!"
    logger.info("TC_SIGNUP_04 - PASSED!")


# ============================================================
# 2. 'LAST STEP' UI, REFERRAL VALIDATION & BACK BUTTON FLOWS
#    (Inspects Last step without finalizing account creation)
# ============================================================

@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_05: Verify 'Complete sign up' button disabled until required fields filled")
@allure.severity(allure.severity_level.NORMAL)
def test_signup_05_complete_button_state_on_last_step(clean_signup_driver) -> None:
    """
    TC_SIGNUP_05:
    On 'Last step', verify 'Complete sign up' is disabled when fields are empty,
    and becomes enabled after filling First name, Last name, and Email (without submitting).
    """
    logger.info("Executing TC_SIGNUP_05: Verify 'Complete sign up' button state...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP, timeout=35)

    verify_on_last_step_screen(clean_signup_driver)
    assert not is_complete_sign_up_enabled(clean_signup_driver), (
        "UI ERROR: 'Complete sign up' should be disabled when required fields are empty!"
    )

    fill_last_step_account_info(
        clean_signup_driver,
        first_name="Kieu",
        last_name="Nguyen",
        email=TEST_EMAIL,
        referral_code=None,
        submit=False,
    )
    assert is_complete_sign_up_enabled(clean_signup_driver), (
        "UI ERROR: 'Complete sign up' should be enabled after filling all required fields!"
    )
    logger.info("TC_SIGNUP_05 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_06: Invalid Referral/Gift Code on Last step -> Error shown")
@allure.severity(allure.severity_level.NORMAL)
def test_signup_06_invalid_referral_code(clean_signup_driver) -> None:
    """
    TC_SIGNUP_06 (AC6 - Invalid referral code):
    Reach 'Last step' screen -> Enter invalid referral code & click Apply -> Verify error shown.
    """
    logger.info("Executing TC_SIGNUP_06: Invalid referral code on Last step...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    verify_on_last_step_screen(clean_signup_driver)
    apply_referral_code_on_last_step(clean_signup_driver, INVALID_REFERRAL_CODE)
    verify_error_shown_and_not_progressed(
        clean_signup_driver,
        stay_Element_xpath="//*[@text='Last step']"
    )
    logger.info("TC_SIGNUP_06 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_07: Click 'Change' on pre-filled FREE250MB card to apply another Referral Code")
@allure.severity(allure.severity_level.NORMAL)
def test_signup_07_change_prefilled_offer_code_on_last_step(clean_signup_driver) -> None:
    """
    TC_SIGNUP_07:
    1. On 'Last step', press Back -> Click 'Claim my offer' so 'FREE250MB' (Applied) is pre-filled.
    2. Click 'Change' next to Referral/gift code -> Enter a different valid referral code and click 'Apply'.
    """
    logger.info("Executing TC_SIGNUP_07: Click 'Change' on pre-filled FREE250MB card...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    verify_on_last_step_screen(clean_signup_driver)
    tap_back_on_last_step(clean_signup_driver)
    handle_last_step_retention_offer(clean_signup_driver, claim_offer=True)

    apply_referral_code_on_last_step(clean_signup_driver, VALID_REFERRAL_CODE)
    logger.info("TC_SIGNUP_07 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_08: Back on Last step -> 'No, I don't want the offer' -> Returns to Sign Up screen")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_08_last_step_back_decline_offer(clean_signup_driver) -> None:
    """
    TC_SIGNUP_08 (Branch 2 - Press Back on Last step -> No, I don't want the offer):
    1. Reach 'Last step' screen.
    2. Tap Back ('<-') -> Verify 'Your free data is waiting' retention screen appears.
    3. Click 'No, I don't want the offer' -> Verify exits 'Last step' back to Sign Up screen, user NOT on Home.
    """
    logger.info("Executing TC_SIGNUP_08: Back on Last step -> No, I don't want the offer...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    verify_on_last_step_screen(clean_signup_driver)
    tap_back_on_last_step(clean_signup_driver)
    handle_last_step_retention_offer(clean_signup_driver, claim_offer=False)
    logger.info("TC_SIGNUP_08 - PASSED!")


# ============================================================
# 3. SUCCESSFUL SIGN-UP COMPLETION FLOWS & ALREADY REGISTERED PHONE CHECK
# ============================================================

@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_09: Back on Last step -> 'Claim my offer' -> Auto-applies FREE250MB -> Complete sign up")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_09_last_step_back_claim_offer_and_complete(clean_signup_driver) -> None:
    """
    TC_SIGNUP_09 (Branch 1 - Press Back on Last step -> Claim my offer -> Complete sign up):
    1. Reach 'Last step' screen.
    2. Tap Back ('<-') -> Verify 'Your free data is waiting' retention screen appears.
    3. Click 'Claim my offer' -> Verify return to 'Last step' with 'FREE250MB' ('✓ Applied') pre-filled.
    4. Fill First name, Last name, Email -> Click 'Complete sign up' -> Verify Home screen.
    """
    logger.info("Executing TC_SIGNUP_09: Back on Last step -> Claim my offer (FREE250MB) -> Complete...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    verify_on_last_step_screen(clean_signup_driver)
    tap_back_on_last_step(clean_signup_driver)
    handle_last_step_retention_offer(clean_signup_driver, claim_offer=True)

    fill_last_step_account_info(
        clean_signup_driver,
        first_name="Kieu",
        last_name="Nguyen",
        email=TEST_EMAIL,
        referral_code=None,  # Keep pre-filled FREE250MB
        submit=True,
    )
    verify_home_screen_after_signup(clean_signup_driver, check_signup_offer=True)
    logger.info("TC_SIGNUP_09 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_10: Sign up with a valid Referral/Gift Code on Last step -> Complete -> Home")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_10_success_with_valid_referral_code(clean_signup_driver) -> None:
    """
    TC_SIGNUP_10 (AC6 - Valid code):
    Sign up with TEST_MOBILE -> OTP -> Enter valid referral code & Apply -> Complete sign up -> Home.
    """
    logger.info("Executing TC_SIGNUP_10: Sign up with valid referral code...")
    dismiss_account_suspended_popup(clean_signup_driver, timeout=3)
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    fill_last_step_account_info(
        clean_signup_driver,
        first_name="Kieu",
        last_name="Nguyen",
        email=TEST_EMAIL,
        referral_code=VALID_REFERRAL_CODE,
        submit=True,
    )
    verify_home_screen_after_signup(clean_signup_driver, check_signup_offer=True)
    logger.info("TC_SIGNUP_10 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_11: Sign up with a new Email -> OTP -> Last step -> Home")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_11_success_with_new_email(clean_signup_driver) -> None:
    """
    TC_SIGNUP_11 (AC1, AC7):
    Sign up with TEST_EMAIL (reset via API before test) -> Verify OTP -> Fill 'Last step' account info -> Land on Home.
    """
    logger.info("Executing TC_SIGNUP_11: Sign up with new email...")
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_email(clean_signup_driver)
    enter_email_and_submit(clean_signup_driver, TEST_EMAIL)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    fill_last_step_account_info(
        clean_signup_driver,
        first_name="Kieu",
        last_name="Nguyen",
        email=TEST_EMAIL,
        referral_code=None,
        submit=True,
    )
    verify_home_screen_after_signup(clean_signup_driver, check_signup_offer=True)
    logger.info("TC_SIGNUP_11 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_12: Sign up with a new Mobile Number -> OTP -> Last step -> Home")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_12_success_with_new_phone(clean_signup_driver) -> None:
    """
    TC_SIGNUP_12 (AC2, AC7):
    Sign up with TEST_MOBILE (372217263) -> Verify OTP -> Fill 'Last step' account info -> Land on Home.
    (Leaves TEST_MOBILE registered on backend so TC_SIGNUP_13 can immediately verify already-registered phone).
    """
    logger.info("Executing TC_SIGNUP_12: Sign up with new mobile number...")
    dismiss_account_suspended_popup(clean_signup_driver, timeout=3)
    open_signup_gate_from_onboarding(clean_signup_driver)
    select_continue_with_mobile(clean_signup_driver)
    select_country_code(clean_signup_driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(clean_signup_driver, TEST_MOBILE, request_otp_channel=True)
    input_otp_code(clean_signup_driver, TestConfig.OTP)

    fill_last_step_account_info(
        clean_signup_driver,
        first_name="Kieu",
        last_name="Nguyen",
        email=TEST_EMAIL,
        referral_code=None,
        submit=True,
    )
    verify_home_screen_after_signup(clean_signup_driver, check_signup_offer=True)
    logger.info("TC_SIGNUP_12 - PASSED!")


@allure.feature("Sign Up (ESKIMO-886)")
@allure.story("TC_SIGNUP_13: Already registered Phone Number (after successful sign-up) -> Error shown")
@allure.severity(allure.severity_level.NORMAL)
def test_signup_13_already_registered_phone(driver) -> None:
    """
    TC_SIGNUP_13 (AC5 - Already registered Phone):
    Runs right after TC_SIGNUP_12 (where TEST_MOBILE 372217263 was registered) WITHOUT resetting the backend account.
    Attempt Sign Up again with TEST_MOBILE -> Verify error/blocked progression and user not logged in.
    """
    logger.info(f"Executing TC_SIGNUP_13: Already registered phone number (after TC_SIGNUP_12: {TEST_MOBILE})...")

    open_signup_gate_from_onboarding(driver)
    select_continue_with_mobile(driver)
    select_country_code(driver, TestConfig.COUNTRY_SEARCH)
    enter_mobile_and_submit(driver, TEST_MOBILE, request_otp_channel=True)

    verify_error_shown_and_not_progressed(
        driver,
        stay_Element_xpath="//*[@resource-id='travel.eskimo.esim.uat:id/et_mobile_number']"
    )
    home_elems = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home")
    assert len(home_elems) == 0, "ERROR: User should not be logged in with already registered phone on Sign Up!"
    logger.info("TC_SIGNUP_13 - PASSED!")


# @allure.feature("Sign Up (ESKIMO-886)")
# @allure.story("API Reset Mobile & Email Account for Reusable Sign Up")
# @allure.severity(allure.severity_level.NORMAL)
# def test_reset_mobile_account(driver) -> None:
#     """
#     Standalone utility test to reset TEST_MOBILE (372217263) and TEST_EMAIL (kieu.signup.auto@yopmail.com)
#     via Eskimo Stage API.
#     """
#     api = ApiHelper()
#     res_mobile = api.reset_mobile_account(TEST_MOBILE)
#     res_email = api.reset_email_account(TEST_EMAIL)
#     logger.info(f"Reset mobile account result: {res_mobile}")
#     logger.info(f"Reset email account result: {res_email}")
#     assert res_mobile.get("status_code") == 200, f"Reset mobile account failed: {res_mobile}"


