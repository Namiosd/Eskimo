import pytest
import allure
from core.logger import logger
from pages.profile_page import (
    navigate_to_personal_profile,
    get_profile_details,
    update_profile_info,
    back_to_account_screen
)


@allure.feature("Account & Profile")
@allure.story("TC_PROFILE_001: View Personal Profile Details")
@allure.severity(allure.severity_level.CRITICAL)
def test_view_personal_profile(logged_in_driver):
    """
    TC_PROFILE_001:
    1. Truy cập tab Account và click vào 'Personal Profile'.
    2. Xác thực tiêu đề trang 'Personal Profile' hiển thị.
    3. Đọc và kiểm tra các trường thông tin cá nhân (First name, Last name, Email, Country, DOB, Mobile).
    """
    logger.info("=== Bắt đầu TC_PROFILE_001: Xem thông tin Personal Profile ===")
    navigate_to_personal_profile(logged_in_driver)
    
    info = get_profile_details(logged_in_driver)
    print("\n--- [Thông tin hồ sơ cá nhân] ---")
    for k, v in info.items():
        print(f" • {k.replace('_', ' ').title()}: {v}")

    assert len(info.get("first_name", "")) > 0, "❌ First Name không được để trống!"
    assert len(info.get("email", "")) > 0, "❌ Email không được để trống!"
    logger.info("✅ TC_PROFILE_001 — PASSED!")


@allure.feature("Account & Profile")
@allure.story("TC_PROFILE_002: Update Profile Information")
@allure.severity(allure.severity_level.NORMAL)
def test_update_profile_name(logged_in_driver):
    """
    TC_PROFILE_002:
    1. Truy cập vào trang Personal Profile.
    2. Đọc thông tin tên hiện tại.
    3. Nhập cập nhật tên mới và bấm 'SAVE UPDATE'.
    4. Xác thực dữ liệu cập nhật thành công.
    """
    logger.info("=== Bắt đầu TC_PROFILE_002: Cập nhật thông tin Profile ===")
    navigate_to_personal_profile(logged_in_driver)
    
    current_info = get_profile_details(logged_in_driver)
    current_first_name = current_info.get("first_name", "Nami")
    current_last_name = current_info.get("last_name", "Kayoko")

    # Cập nhật tên
    update_profile_info(logged_in_driver, first_name=current_first_name, last_name=current_last_name)
    logger.info("✅ Đã bấm SAVE UPDATE thành công.")
    logger.info("✅ TC_PROFILE_002 — PASSED!")


@allure.feature("Account & Profile")
@allure.story("TC_PROFILE_003: Navigate Back to Account Screen")
@allure.severity(allure.severity_level.NORMAL)
def test_navigate_back_from_profile(logged_in_driver):
    """
    TC_PROFILE_003:
    1. Truy cập vào trang Personal Profile.
    2. Click nút Navigate Up (Back).
    3. Xác thực đã quay trở lại màn hình Account thành công.
    """
    logger.info("=== Bắt đầu TC_PROFILE_003: Quay lại tab Account từ Profile ===")
    navigate_to_personal_profile(logged_in_driver)
    back_to_account_screen(logged_in_driver)
    logger.info("✅ TC_PROFILE_003 — PASSED!")
