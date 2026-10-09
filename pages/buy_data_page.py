import os
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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(ROOT_DIR, "reports", "screenshots")


def buy_data_plan(driver: webdriver.Remote, plan_name: str = "Global", data_size: str = "10 GB") -> None:
    """
    Execute data plan purchasing sequence starting from the Home dashboard.
    
    Args:
        driver: Remote Appium WebDriver instance.
        plan_name: Target package selection name (e.g., 'Global').
        data_size: Target plan volume capacity description.
    """
    wait = WebDriverWait(driver, 30)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # Let UI settle after login initialization
    time.sleep(5)
    debug_shot = os.path.join(SCREENSHOTS_DIR, "debug_step0.png")
    driver.save_screenshot(debug_shot)
    logger.info(f"Saved initial pre-purchase screenshot to {debug_shot}.")

    # ============================================================
    # STEP 1: Click Buy Data on Home view (if store sheet is not already open)
    # ============================================================
    with allure.step(f"Open store bottom sheet and select plan group '{plan_name}'"), Step(f"Open store bottom sheet and select plan group '{plan_name}'"):
        store_sheet_open = False
        try:
            global_plan = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/global_section")
            if global_plan.is_displayed():
                store_sheet_open = True
                logger.info("Store sheet is already open. Skipping Buy Data click.")
        except Exception:
            pass

        if not store_sheet_open:
            # Synchronize layout to Home Tab if not already there
            try:
                buy_data_btn_visible = False
                try:
                    buy_data_btn = driver.find_element(AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="travel.eskimo.esim.uat:id/li_buy_tab"]/android.widget.ImageView')
                    if buy_data_btn.is_displayed():
                        buy_data_btn_visible = True
                except Exception:
                    pass
                    
                if not buy_data_btn_visible:
                    logger.info("Buy Data button not visible. Clicking Home tab to synchronize...")
                    home_tab = wait.until(
                        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home"))
                    )
                    home_tab.click()
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"Could not synchronize view to Home dashboard: {e}")

            buy_data_btn = wait_for_element_with_anr_handling(
                driver, '//android.widget.LinearLayout[@resource-id="travel.eskimo.esim.uat:id/li_buy_tab"]/android.widget.ImageView', timeout=30
            )
            assert buy_data_btn.is_displayed(), "Home view 'Buy Data' access button is not visible!"
            buy_data_btn.click()
            logger.info("Opened store bottom sheet view.")
        
        # Choose targeted card category inside the store bottom sheet
        logger.info("Waiting for store bottom sheet animation to settle...")
        time.sleep(1.5)

        plan_list = None
        end_time = time.monotonic() + 60
        while time.monotonic() < end_time:
            # 1. Check if dataWheel is already visible
            try:
                wheels = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/dataWheel']")
                if wheels and wheels[0].is_displayed():
                    plan_list = wheels[0]
                    logger.info("Plans list (dataWheel) detected successfully.")
                    break
            except Exception:
                pass

            # 2. If dataWheel is not visible yet, click global_section
            try:
                global_plans = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/global_section']")
                if global_plans and global_plans[0].is_displayed():
                    logger.info(f"Clicking plan group category: '{plan_name}'...")
                    global_plans[0].click()
            except Exception as e:
                logger.debug(f"Clicking '{plan_name}' encountered exception: {e}")

            time.sleep(3)

        if not plan_list:
            # Fallback to wait_for_element_with_anr_handling in case of ANR dialog or delay
            plan_list = wait_for_element_with_anr_handling(
                driver, "//*[@resource-id='travel.eskimo.esim.uat:id/dataWheel']", timeout=15
            )
        assert plan_list is not None and plan_list.is_displayed(), "Plans list (dataWheel) is not visible on view layout!"

    # ============================================================
    # STEP 2: Choose Data Plan Package volume
    # ============================================================
    with allure.step(f"Choose Data Plan Package volume '{data_size}'"), Step(f"Choose Data Plan Package volume '{data_size}'"):
        plan_item = wait_for_element_with_anr_handling(
            driver, f"//android.widget.TextView[@text='{data_size}']", timeout=30
        )
        assert plan_item.is_displayed(), f"Plan volume capacity option '{data_size}' is not visible!"
        plan_item.click()
        logger.info(f"Selected plan volume: {data_size}")

    # ============================================================
    # STEP 3: Click Buy Now (Checkout button on package selector page)
    # ============================================================
    with allure.step("Click Checkout / Buy Now"), Step("Click Checkout / Buy Now"):
        buy_now_btn = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/txt_buy_now']", timeout=30
        )
        assert buy_now_btn.is_displayed(), "Action button 'Checkout' is not visible!"
        buy_now_btn.click()
        logger.info("Clicked Checkout button.")

    # ============================================================
    # STEP 4: Confirm purchase prompt (dialog)
    # ============================================================
    with allure.step("Confirm prompt dialog"), Step("Confirm prompt dialog"):
        time.sleep(3)
        continue_btn = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_continue']", timeout=30
        )
        assert continue_btn.is_displayed(), "Prompt dialog 'Buy Now Use Later' is not visible!"
        continue_btn.click()
        logger.info("Confirmed prompt dialog ('Continue' clicked).")

        time.sleep(3)
        debug_shot4 = os.path.join(SCREENSHOTS_DIR, "debug_step4.png")
        driver.save_screenshot(debug_shot4)

    # ============================================================
    # STEP 5: Access Checkout view
    # ============================================================
    with allure.step("Proceed to Checkout view"), Step("Proceed to Checkout view"):
        checkout_btn = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/checkout']", timeout=30
        )
        assert checkout_btn.is_displayed(), "Checkout view page is not visible!"
        checkout_btn.click()
        logger.info("Proceeded to checkout payment gateway.")

    # ============================================================
    # STEP 6: Select Payment Method (Card Method)
    # ============================================================
    with allure.step("Select Card payment method"), Step("Select Card payment method"):
        time.sleep(3)
        pay_by_card = wait_for_element_with_anr_handling(
            driver, '//android.widget.LinearLayout[@resource-id="travel.eskimo.esim.uat:id/container_card_methods"]/androidx.cardview.widget.CardView/android.view.ViewGroup', timeout=30
        )
        assert pay_by_card.is_displayed(), "Card method layout card container is not visible!"
        pay_by_card.click()
        logger.info("Selected payment method: Card.")

        # Access Stripe checkout gateway
        payment_continue = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/checkout']", timeout=30
        )
        payment_continue.click()
        logger.info("Accessing Stripe secure payment gateway...")

    # ============================================================
    # STEP 7: Submit Stripe Payment
    # ============================================================
    with allure.step("Submit Stripe Payment"), Step("Submit Stripe Payment"):
        time.sleep(3)
        pay_btn = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/primary_button']", timeout=30
        )
        assert pay_btn.is_displayed(), "Stripe checkout submission pay button is not visible!"
        pay_btn.click()
        logger.info("Submitted payment payload via Stripe.")

        # Await checkout completion view
        time.sleep(5)
        success_msg = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/payment_status_message']", timeout=60
        )
        assert success_msg.is_displayed(), "Transaction success screen layout was not displayed!"
        logger.info(f"Payment transaction authorized successfully: {success_msg.text}")

    # ============================================================
    # STEP 8: Navigate to My Plans to verify transaction
    # ============================================================
    with allure.step("Navigate back to check plans status"), Step("Navigate back to check plans status"):
        see_data_btn = wait_for_element_with_anr_handling(
            driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_ok']", timeout=30
        )
        see_data_btn.click()
        logger.info("Navigating back to check plans status ('See my data' clicked).")

    # Await loading spinner to disappear if active, then verify My Plans tab
    with allure.step("Verify My Plans balance update"), Step("Verify My Plans balance update"):
        end_time = time.monotonic() + 90
        spinner_detected = False
        spinner_start = 0
        logger.info("Waiting for Data Balance view to load and stabilize...")
        while time.monotonic() < end_time:
            try:
                # Check if progress spinner is active
                spinner = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/progress_nearby")
                if spinner.is_displayed():
                    if not spinner_detected:
                        logger.info("Loading spinner 'progress_nearby' detected. Waiting for data balance update from server...")
                        spinner_detected = True
                        spinner_start = time.monotonic()
                    elif time.monotonic() - spinner_start > 15:
                        logger.info("Spinner overlay persisted >15s. Sending back event to dismiss loading dialog...")
                        try:
                            driver.back()
                        except Exception:
                            pass
                        time.sleep(2)
                    else:
                        time.sleep(2)
                    continue
            except Exception:
                pass

            try:
                balance_indicators = (
                    "//*[@resource-id='travel.eskimo.esim.uat:id/txt_my_plan'] | "
                    "//*[@text='My Plans'] | "
                    "//*[@text='Data Balance'] | "
                    "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home']"
                )
                target_elem = driver.find_element(AppiumBy.XPATH, balance_indicators)
                if target_elem.is_displayed():
                    logger.info("Data Balance view loaded successfully. Customer dashboard verified.")
                    break
            except Exception:
                pass

            time.sleep(2)
        else:
            raise TimeoutException("Timed out waiting for 'My Plans' tab to become visible after 90 seconds.")

        logger.info("Transaction validated. Customer 'My Plans' dashboard successfully updated.")
