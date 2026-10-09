import pytest
import allure
from core.logger import logger
from pages.referral_page import (
    navigate_to_refer_friend,
    open_and_verify_how_it_works,
    open_and_verify_my_referrals,
    click_invite_and_dismiss_share
)


@allure.feature("Refer a Friend")
@allure.story("TC_REFERRAL_001: Access Refer a Friend from Home Card and Verify Code")
@allure.severity(allure.severity_level.CRITICAL)
def test_refer_friend_from_home(logged_in_driver):
    """
    TC_REFERRAL_001: 
    1. Từ màn hình Home, click vào thẻ 'Refer a friend, you both get 500MB'.
    2. Xác thực điều hướng đến màn hình Refer a Friend (Rewards - Free data).
    3. Kiểm tra mã giới thiệu (Referral Code) hiển thị hợp lệ.
    """
    logger.info("=== Bắt đầu TC_REFERRAL_001: Truy cập Refer a Friend từ Home ===")
    ref_code = navigate_to_refer_friend(logged_in_driver)
    print(f"\n Mã Referral Code của tài khoản: {ref_code}")
    assert len(ref_code) > 0, "❌ Mã Referral Code không hợp lệ!"
    logger.info("✅ TC_REFERRAL_001 — PASSED!")


@allure.feature("Refer a Friend")
@allure.story("TC_REFERRAL_002: View 'How it works' Details")
@allure.severity(allure.severity_level.NORMAL)
def test_refer_friend_how_it_works(logged_in_driver):
    """
    TC_REFERRAL_002:
    1. Điều hướng đến màn hình Refer a Friend.
    2. Click 'How it works' để mở hướng dẫn chi tiết thể lệ chương trình.
    3. Đóng popup hướng dẫn và quay lại màn hình chính.
    """
    logger.info("=== Bắt đầu TC_REFERRAL_002: Kiểm tra 'How it works' ===")
    navigate_to_refer_friend(logged_in_driver)
    open_and_verify_how_it_works(logged_in_driver)
    logger.info("✅ TC_REFERRAL_002 — PASSED!")


@allure.feature("Refer a Friend")
@allure.story("TC_REFERRAL_003: View 'My Referrals' Statistics")
@allure.severity(allure.severity_level.NORMAL)
def test_refer_friend_my_referrals(logged_in_driver):
    """
    TC_REFERRAL_003:
    1. Điều hướng đến màn hình Refer a Friend.
    2. Click 'My Referrals' để mở màn hình thống kê danh sách bạn bè đã mời.
    3. Đọc và xác thực các chỉ số (Pending, Referrals, Data earned).
    4. Quay lại màn hình Refer a Friend.
    """
    logger.info("=== Bắt đầu TC_REFERRAL_003: Kiểm tra màn hình 'My Referrals' ===")
    navigate_to_refer_friend(logged_in_driver)
    stats = open_and_verify_my_referrals(logged_in_driver)
    print(f"\n📊 Thống kê Referrals: {stats}")
    logger.info("✅ TC_REFERRAL_003 — PASSED!")


@allure.feature("Refer a Friend")
@allure.story("TC_REFERRAL_004: Click Invite to Share Referral Code")
@allure.severity(allure.severity_level.NORMAL)
def test_refer_friend_invite(logged_in_driver):
    """
    TC_REFERRAL_004:
    1. Điều hướng đến màn hình Refer a Friend.
    2. Click nút 'Invite'.
    3. Kiểm tra hộp thoại chia sẻ của hệ thống (Share Sheet) xuất hiện và đóng lại an toàn.
    """
    logger.info("=== Bắt đầu TC_REFERRAL_004: Kiểm tra nút 'Invite' ===")
    navigate_to_refer_friend(logged_in_driver)
    click_invite_and_dismiss_share(logged_in_driver)
    logger.info("✅ TC_REFERRAL_004 — PASSED!")
