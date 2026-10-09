import allure
import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

from core.logger import logger
from core.step_tracker import Step
from pages.base_page import wait_for_element_with_anr_handling


def navigate_to_account(driver: webdriver.Remote) -> None:
    """Điều hướng đến tab Account từ bất kỳ màn hình nào."""
    account_tab = wait_for_element_with_anr_handling(
        driver,
        "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_account']",
        timeout=20
    )
    account_tab.click()
    time.sleep(1)
    logger.info("Navigate: Đã chuyển đến tab Account.")


def navigate_to_personal_profile(driver: webdriver.Remote) -> None:
    """
    Từ tab Account, mở trang Personal Profile và xác thực trang tải hoàn tất.
    """
    # Bước 1: Đảm bảo đang ở tab Account
    navigate_to_account(driver)

    # Bước 2: Click vào mục Personal Profile
    with allure.step("Click 'Personal Profile' on Account screen"), Step("Click 'Personal Profile' on Account screen"):
        profile_item = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/txt_personal_profile'] | //*[@text='Personal Profile']",
            timeout=20
        )
        assert profile_item.is_displayed(), "❌ Không tìm thấy mục 'Personal Profile' trên tab Account!"
        profile_item.click()
        logger.info("Action: Đã click vào mục 'Personal Profile'.")

    # Bước 3: Chờ màn hình Personal Profile tải xong
    with allure.step("Verify Personal Profile screen is loaded"), Step("Verify Personal Profile screen is loaded"):
        title_elem = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/toolbar_title' and @text='Personal Profile']",
            timeout=20
        )
        assert title_elem.is_displayed(), "❌ Tiêu đề 'Personal Profile' không hiển thị!"
        logger.info("Verify: Màn hình Personal Profile đã tải thành công.")


def get_profile_details(driver: webdriver.Remote) -> dict:
    """
    Đọc toàn bộ thông tin chi tiết của người dùng trên trang Personal Profile.
    
    Returns:
        dict chứa các thông tin: first_name, last_name, email, country, dob, gender, phone, verified_status.
    """
    info = {}
    with allure.step("Read profile details from screen"), Step("Read profile details from screen"):
        try:
            info["first_name"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_first_name").text.strip()
        except Exception:
            info["first_name"] = ""

        try:
            info["last_name"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_last_name").text.strip()
        except Exception:
            info["last_name"] = ""

        try:
            info["email"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_billing_email").text.strip()
        except Exception:
            info["email"] = ""

        try:
            info["country"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/et_country").text.strip()
        except Exception:
            info["country"] = ""

        try:
            info["dob"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_date_of_birth").text.strip()
        except Exception:
            info["dob"] = ""

        try:
            info["gender"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_gender").text.strip()
        except Exception:
            info["gender"] = ""

        try:
            phone_num = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/mobile_number").text.strip()
            country_code = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code").text.strip()
            info["mobile"] = f"{country_code} {phone_num}"
        except Exception:
            info["mobile"] = ""

        try:
            info["verified_status"] = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_verified").text.strip()
        except Exception:
            info["verified_status"] = ""

        logger.info(f"Verify Profile Info: {info}")
        return info


def update_profile_info(driver: webdriver.Remote, first_name: str = None, last_name: str = None) -> None:
    """
    Cập nhật tên / họ trên trang Personal Profile và bấm 'SAVE UPDATE'.
    """
    with allure.step("Update profile fields"), Step("Update profile fields"):
        if first_name is not None:
            fn_elem = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/et_first_name']", timeout=15)
            fn_elem.clear()
            fn_elem.send_keys(first_name)
            logger.info(f"Action: Đã nhập First Name: '{first_name}'")

        if last_name is not None:
            ln_elem = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/et_last_name']", timeout=15)
            ln_elem.clear()
            ln_elem.send_keys(last_name)
            logger.info(f"Action: Đã nhập Last Name: '{last_name}'")

    # Ẩn bàn phím nếu đang hiển thị
    try:
        driver.hide_keyboard()
    except Exception:
        pass

    time.sleep(1)

    with allure.step("Click 'SAVE UPDATE' button"), Step("Click 'SAVE UPDATE' button"):
        btn_update = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/btn_update'] | //*[@text='SAVE UPDATE']",
            timeout=20
        )
        assert btn_update.is_displayed(), "❌ Không tìm thấy nút 'SAVE UPDATE'!"
        btn_update.click()
        logger.info("Action: Đã click nút 'SAVE UPDATE'.")
        time.sleep(3)


def back_to_account_screen(driver: webdriver.Remote) -> None:
    """
    Click nút Navigate Up (Back) để quay trở lại tab Account.
    """
    with allure.step("Click Back to return to Account screen"), Step("Click Back to return to Account screen"):
        try:
            back_btn = driver.find_elements(AppiumBy.XPATH, "//android.widget.ImageButton[@content-desc='Navigate up']")
            if back_btn and back_btn[0].is_displayed():
                back_btn[0].click()
            else:
                driver.back()
        except Exception:
            driver.back()

        time.sleep(2)
        # Xác nhận đã quay lại màn hình Account
        account_header = wait_for_element_with_anr_handling(
            driver,
            "//*[@resource-id='travel.eskimo.esim.uat:id/txt_personal_profile'] | //*[@resource-id='travel.eskimo.esim.uat:id/lbl_account']",
            timeout=15
        )
        assert account_header.is_displayed(), "❌ Chưa trở về màn hình Account!"
        logger.info("Verify: Đã quay lại màn hình Account thành công.")
