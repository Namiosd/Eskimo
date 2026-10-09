import time
import allure
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from core.logger import logger
from core.step_tracker import Step
from pages.base_page import wait_for_element_with_anr_handling


def navigate_to_home(driver: webdriver.Remote) -> None:
    """Navigate to Home screen from any screen."""
    home_tab = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home']", timeout=20)
    home_tab.click()
    time.sleep(1)
    logger.info("Navigate: Returned to Home screen successfully.")


def redeem_voucher(driver: webdriver.Remote, voucher_code: str) -> str:
    """
    Redeem voucher code - automatically detect valid or invalid status after applying.

    TC_REDEEM_001: Valid code   -> Redeem data plan screen -> Redeem now -> Success -> PASSED
    TC_REDEEM_002: Invalid code -> Error popup -> Okay -> Back to Vouchers -> PASSED

    Precondition: Logged in, app on any screen.
    """
    # ============================================================
    # NAVIGATE: Back to Home first
    # ============================================================
    navigate_to_home(driver)

    # ============================================================
    # WAIT FOR UI: Wait for skeleton loading layout to disappear
    # ============================================================
    try:
        skeleton_id = "travel.eskimo.esim.uat:id/skeleton_loading_layout"
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((AppiumBy.ID, skeleton_id))
        )
        logger.info("Skeleton loading layout detected. Waiting for home dashboard content to load...")
        WebDriverWait(driver, 60).until_not(
            EC.presence_of_element_located((AppiumBy.ID, skeleton_id))
        )
        logger.info("Skeleton loading layout disappeared. Home dashboard loaded.")
    except Exception:
        logger.info("No skeleton loading layout detected. Proceeding...")

    # ============================================================
    # STEP 1: Click Vouchers card (Wait up to 60s for loading stability)
    # ============================================================
    with allure.step("Click Vouchers card"), Step("Click Vouchers card"):
        vouchers_card = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/redeem_card']", timeout=60)
        assert vouchers_card.is_displayed(), "Vouchers card not visible!"
        logger.info("Check UI: Vouchers card is displayed.")
        vouchers_card.click()
        logger.info("Action: Clicked Vouchers card.")

    # ============================================================
    # STEP 2: Enter voucher code
    # ============================================================
    with allure.step(f"Enter voucher code '{voucher_code}'"), Step(f"Enter voucher code '{voucher_code}'"):
        code_input = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/txt_promo_code']", timeout=20)
        assert code_input.is_displayed(), "Vouchers screen not visible!"
        logger.info("Verify: Vouchers screen is displayed.")
        code_input.clear()
        code_input.send_keys(voucher_code)
        logger.info(f"Action: Entered voucher code: {voucher_code}")

    # ============================================================
    # STEP 3: Click Apply
    # ============================================================
    with allure.step("Click Apply"), Step("Click Apply"):
        apply_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/txt_apply_code']", timeout=20)
        apply_btn.click()
        logger.info("Action: Clicked Apply.")

    # ============================================================
    # DETECT: Valid or Invalid?
    # ============================================================
    with allure.step("Detect code validity status"), Step("Detect code validity status"):
        time.sleep(2)
        is_valid = False
        try:
            wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_redeem']", timeout=5)
            is_valid = True
        except TimeoutException:
            is_valid = False

    # ============================================================
    # TC_REDEEM_001: Valid Code
    # ============================================================
    if is_valid:
        logger.info("Detect: Code is valid -> running TC_REDEEM_001")

        # Step 5: Click Redeem now
        with allure.step("(Valid Code): Click Redeem now"), Step("(Valid Code): Click Redeem now"):
            redeem_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_redeem']", timeout=20)
            redeem_btn.click()
            logger.info("Action: Clicked Redeem now.")

        # Step 6: Click Continue (popup)
        with allure.step("(Valid Code): Click Continue on popup"), Step("(Valid Code): Click Continue on popup"):
            continue_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_continue']", timeout=20)
            assert continue_btn.is_displayed(), "Popup Buy Now Use Later not visible!"
            logger.info("Verify: Popup Buy Now Use Later is displayed.")
            continue_btn.click()
            logger.info("Action: Clicked Continue.")

        # Step 7: Verify success
        with allure.step("(Valid Code): Verify success screen"), Step("(Valid Code): Verify success screen"):
            success_msg = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/header']", timeout=20)
            assert success_msg.is_displayed(), "Success screen not visible!"
            logger.info(f"Verify: Success message: {success_msg.text}")

        # Step 8: Click See my data balance
        with allure.step("(Valid Code): Click See my data balance and verify My Plans tab"), Step("(Valid Code): Click See my data balance and verify My Plans tab"):
            see_data_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_ok']", timeout=20)
            see_data_btn.click()
            logger.info("Action: Clicked See my data balance.")

            time.sleep(2)
            my_plans = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/txt_my_plan']", timeout=20)
            assert my_plans.is_displayed(), "My Plans tab not visible!"
            logger.info("Verify: My Plans tab is displayed - TC_REDEEM_001 PASSED!")
            return "TC_REDEEM_001"

    # ============================================================
    # TC_REDEEM_002: Invalid Code
    # ============================================================
    else:
        logger.info("Detect: Code is invalid -> running TC_REDEEM_002")

        with allure.step("(Invalid Code): Verify oops error popup"), Step("(Invalid Code): Verify oops error popup"):
            oops_icon = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/oops_image']", timeout=20)
            assert oops_icon.is_displayed(), "Oops error icon not visible!"
            logger.info("Verify: Popup 'Sorry, this code is invalid' is displayed correctly")

        with allure.step("(Invalid Code): Dismiss error popup and verify returned to Vouchers"), Step("(Invalid Code): Dismiss error popup and verify returned to Vouchers"):
            okay_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_ok']", timeout=20)
            okay_btn.click()
            logger.info("Action: Clicked Okay - closed error popup")

            time.sleep(1)
            voucher_screen = wait_for_element_with_anr_handling(driver, "//android.widget.TextView[@resource-id='travel.eskimo.esim.uat:id/toolbar_title' and @text='Vouchers']", timeout=20)
            assert voucher_screen.is_displayed(), "Did not navigate back to Vouchers screen!"
            logger.info("Verify: Returned to Vouchers screen - TC_REDEEM_002 PASSED!")
            return "TC_REDEEM_002"
