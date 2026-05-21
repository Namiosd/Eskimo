from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


def navigate_to_home(driver):
    """Navigate về màn hình Home từ bất kỳ màn hình nào."""
    wait = WebDriverWait(driver, 20)
    home_tab = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home"))
    )
    home_tab.click()
    time.sleep(1)
    print("✅ [Navigate] Đã về màn hình Home")


def redeem_voucher(driver, voucher_code):
    """
    Redeem voucher code — tự detect valid hay invalid sau khi Apply.

    TC_REDEEM_001: code hợp lệ   → màn hình Redeem data plan → Redeem now → Success → PASSED
    TC_REDEEM_002: code không hợp lệ → popup lỗi → Okay → về Vouchers → PASSED

    Precondition: Đã login, app đang ở bất kỳ màn hình nào.
    """
    wait = WebDriverWait(driver, 20)

    # ============================================================
    # NAVIGATE: Về Home trước
    # ============================================================
    navigate_to_home(driver)

    # ============================================================
    # BƯỚC 1: Click Vouchers card
    # ============================================================
    vouchers_card = wait.until(
        EC.element_to_be_clickable((AppiumBy.XPATH,
            '//android.widget.FrameLayout[@resource-id="travel.eskimo.esim.uat:id/ticket_card"]/android.view.ViewGroup'))
    )
    assert vouchers_card.is_displayed(), "❌ Không thấy Vouchers card!"
    print("✅ [Check UI] Vouchers card hiển thị")
    vouchers_card.click()
    print("✅ [Action] Đã click Vouchers card")

    # ============================================================
    # BƯỚC 2: Nhập voucher code
    # ============================================================
    code_input = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_promo_code"))
    )
    assert code_input.is_displayed(), "❌ Không thấy màn hình Vouchers!"
    print("✅ [Verify] Màn hình Vouchers hiển thị")
    code_input.clear()
    code_input.send_keys(voucher_code)
    print(f"✅ [Action] Đã nhập voucher code: {voucher_code}")

    # ============================================================
    # BƯỚC 3: Click Apply
    # ============================================================
    apply_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_apply_code"))
    )
    apply_btn.click()
    print("✅ [Action] Đã click Apply")

    # ============================================================
    # DETECT: Valid hay Invalid?
    # ============================================================
    time.sleep(2)
    is_valid = False
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_redeem"))
        )
        is_valid = True
    except TimeoutException:
        is_valid = False

    # ============================================================
    # TC_REDEEM_001: Code hợp lệ
    # ============================================================
    if is_valid:
        print("✅ [Detect] Code hợp lệ → chạy TC_REDEEM_001")

        # Bước 4: Click Redeem now
        redeem_btn = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_redeem")
        redeem_btn.click()
        print("✅ [Action] Đã click Redeem now")

        # Bước 5: Click Continue (popup)
        continue_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_continue"))
        )
        assert continue_btn.is_displayed(), "❌ Không thấy popup Buy Now Use Later!"
        print("✅ [Verify] Popup Buy Now Use Later hiển thị")
        continue_btn.click()
        print("✅ [Action] Đã click Continue")

        # Bước 6: Verify success
        success_msg = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/header"))
        )
        assert success_msg.is_displayed(), "❌ Không thấy màn hình success!"
        print(f"✅ [Verify] Success: {success_msg.text}")

        # Bước 7: Click See my data balance
        see_data_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_ok"))
        )
        see_data_btn.click()
        print("✅ [Action] Đã click See my data balance")

        # Verify: tab My Plans hiển thị
        time.sleep(2)
        my_plans = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_my_plan"))
        )
        assert my_plans.is_displayed(), "❌ Không thấy tab My Plans!"
        print("✅ [Verify] Tab My Plans hiển thị — TC_REDEEM_001 PASSED! ✅")
        return "TC_REDEEM_001"

    # ============================================================
    # TC_REDEEM_002: Code không hợp lệ
    # ============================================================
    else:
        print("✅ [Detect] Code không hợp lệ → chạy TC_REDEEM_002")

        # Verify: popup lỗi hiển thị
        oops_icon = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/oops_image"))
        )
        assert oops_icon.is_displayed(), "❌ Không thấy popup lỗi!"
        print("✅ [Verify] Popup 'Sorry, this code is invalid' hiển thị đúng")

        # Click Okay
        okay_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_ok"))
        )
        okay_btn.click()
        print("✅ [Action] Đã click Okay — đóng popup lỗi")

        # Verify: về lại màn hình Vouchers
        time.sleep(1)
        voucher_screen = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH,
                "//android.widget.TextView[@resource-id='travel.eskimo.esim.uat:id/toolbar_title' and @text='Vouchers']"))
        )
        assert voucher_screen.is_displayed(), "❌ Không về lại màn hình Vouchers!"
        print("✅ [Verify] Về lại màn hình Vouchers — TC_REDEEM_002 PASSED! ✅")
        return "TC_REDEEM_002"
