from helper_login import create_driver
from helper_buy_data import buy_data_plan
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = create_driver()

try:
    # Precondition: đã login, đang ở màn hình Data Dashboard
    time.sleep(3)

    wait = WebDriverWait(driver, 15)

    # ============================================================
    # BƯỚC 1: Click Buy từ Data Dashboard
    # ============================================================
    # Check UI
    buy_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/buy_image_card"))
    )
    assert buy_btn.is_displayed(), "❌ [Bước 1] Không thấy nút Buy!"
    print("✅ [Bước 1 - Check UI] Nút Buy hiển thị")

    # Action
    buy_btn.click()
    print("✅ [Bước 1 - Action] Đã click Buy")

    # Verify
    time.sleep(2)
    print("✅ [Bước 1 - Verify] Chuyển sang trang Home")

    # ============================================================
    # BƯỚC 2-10: Reuse flow Buy Data Plan
    # ============================================================
    buy_data_plan(driver)

    print("\n🎉 TC_BUY_DATA_002 — PASSED!")

except Exception as e:
    print(f"\n❌ TC_BUY_DATA_002 — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")