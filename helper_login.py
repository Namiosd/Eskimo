from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ============================================================
# CẤU HÌNH CHUNG
# ============================================================
APPIUM_URL = "http://127.0.0.1:4723"
PHONE_NUMBER = "372217312"
OTP = "1234"

desired_caps = {
    "platformName": "Android",
    "deviceName": "emulator-5554",
    "automationName": "UiAutomator2",
    "appPackage": "travel.eskimo.esim.uat",
    "appActivity": ".presentation.ui.MainActivity",
    "noReset": True,
    "uiautomator2ServerLaunchTimeout": 60000,
    "uiautomator2ServerInstallTimeout": 60000,
}


class AppiumOptions(ArgOptions):
    @property
    def default_capabilities(self):
        return {}


def create_driver():
    """Tạo Appium driver — kết nối vào emulator."""
    options = AppiumOptions()
    for k, v in desired_caps.items():
        options.set_capability(k, v)
    driver = webdriver.Remote(APPIUM_URL, options=options)
    print("✅ Kết nối emulator thành công!")
    return driver


def login(driver, phone=PHONE_NUMBER, otp=OTP):
    """
    Flow login bằng Mobile Number.
    Pattern: Check UI → Action → Verify
    """
    wait = WebDriverWait(driver, 20)

    # ============================================================
    # BƯỚC 1: Nút Log in
    # ============================================================
    # Check UI: nút Log in có hiển thị không?
    login_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_login"))
    )
    assert login_btn.is_displayed(), "❌ Không thấy nút Log in!"
    print("✅ [Check UI] Nút Log in hiển thị đúng")

    # Action: click Log in
    login_btn.click()
    print("✅ [Action] Đã click Log in")

    # Verify: màn hình Welcome back hiển thị
    welcome = wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@text='Welcome back']"))
    )
    assert welcome.is_displayed(), "❌ Không thấy màn hình Welcome back!"
    print("✅ [Verify] Màn hình Welcome back hiển thị đúng")

    # ============================================================
    # BƯỚC 2: Chọn Continue with Mobile Number
    # ============================================================
    # Check UI: nút Continue with Mobile Number có hiển thị không?
    mobile_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@text='Continue with Mobile Number']"))
    )
    assert mobile_btn.is_displayed(), "❌ Không thấy nút Continue with Mobile Number!"
    print("✅ [Check UI] Nút Continue with Mobile Number hiển thị đúng")

    # Action: click Continue with Mobile Number
    mobile_btn.click()
    print("✅ [Action] Đã click Continue with Mobile Number")

    # Verify: màn hình nhập số điện thoại hiển thị
    phone_screen = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
    )
    assert phone_screen.is_displayed(), "❌ Không thấy màn hình nhập số điện thoại!"
    print("✅ [Verify] Màn hình nhập số điện thoại hiển thị đúng")

    # ============================================================
    # BƯỚC 3: Nhập số điện thoại
    # ============================================================
    # Check UI: field số điện thoại có hiển thị không?
    phone_field = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
    )
    assert phone_field.is_displayed(), "❌ Không thấy field nhập số điện thoại!"
    print("✅ [Check UI] Field số điện thoại hiển thị đúng")

    # Action: nhập số điện thoại
    phone_field.clear()
    phone_field.send_keys(phone)
    print(f"✅ [Action] Đã nhập số điện thoại: {phone}")

    # Verify: nút Continue có active không?
    continue_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_continue"))
    )
    assert continue_btn.is_displayed(), "❌ Không thấy nút Continue!"
    print("✅ [Verify] Nút Continue hiển thị đúng")

    # ============================================================
    # BƯỚC 4: Click Continue
    # ============================================================
    # Action: click Continue
    continue_btn.click()
    print("✅ [Action] Đã click Continue")

    # Verify: bottom sheet chọn kênh nhận OTP hiển thị
    whatsapp_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_whatsapp"))
    )
    assert whatsapp_btn.is_displayed(), "❌ Không thấy bottom sheet chọn kênh OTP!"
    print("✅ [Verify] Bottom sheet chọn kênh OTP hiển thị đúng")

    # ============================================================
    # BƯỚC 5: Chọn WhatsApp
    # ============================================================
    # Check UI: nút WhatsApp có hiển thị không?
    assert whatsapp_btn.is_displayed(), "❌ Không thấy nút WhatsApp!"
    print("✅ [Check UI] Nút WhatsApp hiển thị đúng")

    # Action: click WhatsApp
    whatsapp_btn.click()
    print("✅ [Action] Đã chọn WhatsApp")

    # Verify: màn hình nhập OTP hiển thị
    time.sleep(6)
    otp_field_1 = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/otp1"))
    )
    assert otp_field_1.is_displayed(), "❌ Không thấy màn hình nhập OTP!"
    print("✅ [Verify] Màn hình nhập OTP hiển thị đúng")

    # ============================================================
    # BƯỚC 6: Nhập OTP
    # ============================================================
    # Check UI: 4 ô OTP có hiển thị không?
    for i in range(1, 5):
        otp_box = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, f"travel.eskimo.esim.uat:id/otp{i}"))
        )
        assert otp_box.is_displayed(), f"❌ Không thấy ô OTP {i}!"
    print("✅ [Check UI] 4 ô OTP hiển thị đúng")

    # Action: nhập từng số OTP
    for i, digit in enumerate(otp, start=1):
        otp_field = driver.find_element(AppiumBy.ID, f"travel.eskimo.esim.uat:id/otp{i}")
        otp_field.send_keys(digit)
    print(f"✅ [Action] Đã nhập OTP: {otp}")

    # ============================================================
    # BƯỚC 7: Xử lý Allow notifications (app) — nếu có
    # ============================================================
    time.sleep(2)
    try:
        allow_app_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_allow"))
        )
        assert allow_app_btn.is_displayed(), "❌ Không thấy nút Allow notifications!"
        print("✅ [Check UI] Màn hình Allow notifications hiển thị")
        allow_app_btn.click()
        print("✅ [Action] Đã click Allow notifications (app)")
    except:
        print("ℹ️ Không thấy Allow notifications (app), bỏ qua")

    # ============================================================
    # BƯỚC 8: Xử lý Android permission popup — nếu có
    # ============================================================
    time.sleep(2)
    try:
        allow_system_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button"))
        )
        assert allow_system_btn.is_displayed(), "❌ Không thấy nút Allow (Android)!"
        print("✅ [Check UI] Android permission popup hiển thị")
        allow_system_btn.click()
        print("✅ [Action] Đã click Allow (Android permission)")
    except:
        print("ℹ️ Không thấy Android permission popup, bỏ qua")

    # ============================================================
    # VERIFY CUỐI: Màn hình Home hiển thị = Login thành công
    # ============================================================
    time.sleep(2)
    home_tab = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/navigation_home"))
    )
    assert home_tab.is_displayed(), "❌ Không thấy màn hình Home — Login thất bại!"
    print("✅ [Verify] Màn hình Home hiển thị — Login thành công!")
