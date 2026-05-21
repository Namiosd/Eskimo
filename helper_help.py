from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ============================================================
# LOCATORS
# ============================================================
# Nút Help (dùng chung nhiều màn hình)
BTN_HELP = (AppiumBy.ID, "travel.eskimo.esim.uat:id/help_image_card")

# Verify Help Center
HELP_CENTER_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@text="HELP CENTER"]')


# ============================================================
# HELPER: click_help
# ============================================================
def click_help(driver):
    """
    Click nút Help và verify màn hình Help Center hiển thị.
    Dùng được ở bất kỳ màn hình nào có nút Help.
    Pattern: Check UI → Action → Verify
    """
    wait = WebDriverWait(driver, 15)

    # ----------------------------------------------------------
    # Check UI: nút Help có hiển thị không?
    # ----------------------------------------------------------
    help_btn = wait.until(EC.element_to_be_clickable(BTN_HELP))
    assert help_btn.is_displayed(), "❌ [Help] Không thấy nút Help!"
    print("✅ [Help - Check UI] Nút Help hiển thị")

    # ----------------------------------------------------------
    # Action: click Help
    # ----------------------------------------------------------
    help_btn.click()
    print("✅ [Help - Action] Đã click Help")

    # ----------------------------------------------------------
    # Verify: màn hình Help Center hiển thị
    # ----------------------------------------------------------
    time.sleep(2)
    help_title = wait.until(EC.presence_of_element_located(HELP_CENTER_TITLE))
    assert help_title.is_displayed(), "❌ [Help] Không thấy màn hình Help Center!"
    print("✅ [Help - Verify] Màn hình Help Center hiển thị")
