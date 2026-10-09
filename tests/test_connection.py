import pytest
import allure
from core.step_tracker import Step
from tests.conftest import pre_check_environment
from core.driver_factory import create_driver


def test_appium_connection():
    """
    Kịch bản kiểm tra kết nối hệ thống (Sanity Connection Test).
    1. Xác thực trạng thái cổng mạng Appium Server (4723).
    2. Xác thực xem máy ảo Android (emulator-5554) có Online không.
    3. Khởi tạo thử Appium driver để kiểm tra giao tiếp giữa các thành phần.
    """
    print("\n--- BẮT ĐẦU KIỂM TRA KẾT NỐI HỆ THỐNG ---")
    
    # 1 & 2. Kiểm tra môi trường (Port & ADB)
    with allure.step("Verify system environment setup (Appium server and ADB status)"), Step("Verify system environment setup (Appium server and ADB status)"):
        pre_check_environment()
    
    # 3. Tạo thử driver thực tế
    print("\n[Kiểm tra] Đang gửi yêu cầu khởi tạo session tới Appium...")
    with allure.step("Initialize test Appium remote driver session"), Step("Initialize test Appium remote driver session"):
        driver = None
        try:
            driver = create_driver()
            print("✅ KẾT NỐI THÀNH CÔNG: Appium và Máy ảo hoạt động hoàn hảo!")
        except Exception as e:
            pytest.fail(f"❌ KẾT NỐI THẤT BẠI: Không thể tạo session với Appium! Chi tiết lỗi: {e}")
        finally:
            if driver:
                driver.quit()
                print("✅ Đã giải phóng phiên kết nối thử nghiệm.")

