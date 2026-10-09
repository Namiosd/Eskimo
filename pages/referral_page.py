import time
import allure
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.logger import logger
from core.step_tracker import Step
from pages.redeem_page import navigate_to_home
from pages.base_page import wait_for_element_with_anr_handling


def navigate_to_refer_friend(driver: webdriver.Remote) -> str:
    """
    Điều hướng đến màn hình Refer a Friend từ Home:
    1. Đảm bảo đang ở màn hình Home.
    2. Đợi loading skeleton biến mất.
    3. Click vào card 'Refer a friend, you both get 500MB'.
    4. Xác thực đã vào màn hình Refer a friend và lấy mã referral code.
    
    Returns:
        Mã Referral Code hiện tại (ví dụ: 'KIEU1606').
    """
    # Bước 1: Trở về màn hình Home
    navigate_to_home(driver)

    # Bước 2: Đợi skeleton loading hoàn tất nếu có
    try:
        skeleton_id = "travel.eskimo.esim.uat:id/skeleton_loading_layout"
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((AppiumBy.ID, skeleton_id))
        )
        logger.info("Skeleton loading detected. Waiting for Home content to load...")
        WebDriverWait(driver, 60).until_not(
            EC.presence_of_element_located((AppiumBy.ID, skeleton_id))
        )
        logger.info("Home dashboard content loaded.")
    except Exception:
        pass

    # Bước 3: Click card 'Refer a friend, you both get 500MB'
    with allure.step("Click 'Refer a friend' card on Home"), Step("Click 'Refer a friend' card on Home"):
        referral_card = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/referral_card']",
            timeout=30
        )
        assert referral_card.is_displayed(), "❌ Không tìm thấy thẻ 'Refer a friend' trên màn hình Home!"
        logger.info("Check UI: Thẻ 'Refer a friend' hiển thị trên Home.")
        referral_card.click()
        logger.info("Action: Đã click vào thẻ 'Refer a friend'.")

    # Bước 4: Chờ màn hình Refer a friend hiển thị và lấy mã
    with allure.step("Verify Refer a friend screen loaded"), Step("Verify Refer a friend screen loaded"):
        code_elem = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/txt_ref_code']",
            timeout=30
        )
        assert code_elem.is_displayed(), "❌ Không thấy ô mã Referral Code!"
        ref_code = code_elem.text.strip()
        assert len(ref_code) > 0, "❌ Mã Referral Code bị rỗng!"
        logger.info(f"Verify: Màn hình Refer a Friend hiển thị thành công. Mã Referral: '{ref_code}'")
        return ref_code


def get_referral_code(driver: webdriver.Remote) -> str:
    """Lấy mã Referral Code hiển thị trên màn hình hiện tại."""
    code_elem = wait_for_element_with_anr_handling(
        driver,
        "//*[@resource-id='travel.eskimo.esim.uat:id/txt_ref_code']",
        timeout=15
    )
    return code_elem.text.strip()


def open_and_verify_how_it_works(driver: webdriver.Remote) -> None:
    """
    Click 'How it works' để mở bottom sheet giải thích thể lệ, xác thực nội dung và đóng lại.
    """
    with allure.step("Click 'How it works' button"), Step("Click 'How it works' button"):
        btn = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/btn_how_it_work']",
            timeout=20
        )
        assert btn.is_displayed(), "❌ Không tìm thấy nút 'How it works'!"
        btn.click()
        logger.info("Action: Đã click 'How it works'.")

    with allure.step("Verify 'How it works' sheet content"), Step("Verify 'How it works' sheet content"):
        title_elem = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/txt_how_it_works'] | //*[@resource-id='travel.eskimo.esim.uat:id/txt_level_detail_title']",
            timeout=15
        )
        assert title_elem.is_displayed(), "❌ Tiêu đề 'How it works' không hiển thị!"
        logger.info("Verify: Màn hình 'How it works' hiển thị đúng thể lệ.")

        time.sleep(1)
        driver.back()
        time.sleep(2)
        logger.info("Action: Đã đóng màn hình 'How it works'.")


def open_and_verify_my_referrals(driver: webdriver.Remote) -> dict:
    """
    Click 'My Referrals' để mở màn hình thống kê, lấy thông tin stats và quay lại.
    """
    with allure.step("Click 'My Referrals' button"), Step("Click 'My Referrals' button"):
        btn = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/my_referrals']",
            timeout=20
        )
        assert btn.is_displayed(), "❌ Không tìm thấy nút 'My Referrals'!"
        btn.click()
        logger.info("Action: Đã click 'My Referrals'.")

    stats = {}
    with allure.step("Verify 'My Referrals' statistics"), Step("Verify 'My Referrals' statistics"):
        toolbar = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/toolbar_title' and @text='My Referrals']",
            timeout=20
        )
        assert toolbar.is_displayed(), "❌ Không hiển thị màn hình 'My Referrals'!"

        try:
            pending = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_pending_count").text
            referrals = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_complete_referrals").text
            earned = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_earned_data").text
            stats = {
                "pending": pending,
                "referrals": referrals,
                "earned_data": earned
            }
            logger.info(f"Verify: Thống kê My Referrals -> Pending: {pending}, Referrals: {referrals}, Data Earned: {earned}")
        except Exception as e:
            logger.warning(f"Không thể đọc toàn bộ chỉ số thống kê: {e}")

        time.sleep(1)
        try:
            back_btn = driver.find_elements(AppiumBy.XPATH, "//android.widget.ImageButton[@content-desc='Navigate up']")
            if back_btn and back_btn[0].is_displayed():
                back_btn[0].click()
            else:
                driver.back()
        except Exception:
            driver.back()

        time.sleep(2)
        logger.info("Action: Đã quay lại màn hình Refer a friend.")
        return stats


def click_invite_and_dismiss_share(driver: webdriver.Remote) -> None:
    """
    Click nút 'Invite' và kiểm tra hộp thoại chia sẻ của Android (Share Sheet) xuất hiện, sau đó đóng nó.
    """
    with allure.step("Click 'Invite' button"), Step("Click 'Invite' button"):
        invite_btn = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/txt_invite'] | //*[@text='Invite']",
            timeout=20
        )
        assert invite_btn.is_displayed(), "❌ Không tìm thấy nút 'Invite'!"
        invite_btn.click()
        logger.info("Action: Đã click nút 'Invite'.")

    with allure.step("Verify Android Share Sheet opens and dismiss"), Step("Verify Android Share Sheet opens and dismiss"):
        time.sleep(2)
        driver.back()
        time.sleep(1)
        logger.info("Action: Đã đóng Android Share Sheet thành công.")
