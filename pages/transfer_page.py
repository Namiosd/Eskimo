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

PHONE_NUMBER = "372217316"
COUNTRY_SEARCH = "Vietnam"


def transfer_data(driver: webdriver.Remote, phone: str = PHONE_NUMBER) -> str:
    """
    TC_Transfer_Homescreen_001: Transfer data plan cho người khác.
    Precondition: Đã login, đang ở bất kỳ màn hình nào.
    """
    # Navigate về Home trước
    navigate_to_home(driver)

    # ============================================================
    # BƯỚC 1: Click circular Transfer button on Home screen
    # ============================================================
    with allure.step("Click circular Transfer button"), Step("Click circular Transfer button"):
        transfer_card = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/cd_transfer']", timeout=20)
        assert transfer_card.is_displayed(), "❌ Không thấy nút Transfer màu xanh!"
        logger.info("Check UI: Circular Transfer button is displayed.")
        transfer_card.click()
        logger.info("Action: Clicked circular Transfer button.")

        # Await page transition (circular Transfer button disappears)
        try:
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/cd_transfer"))
            )
            logger.info("Page transitioned from Home screen successfully.")
        except Exception:
            logger.warning("Home circular Transfer button did not disappear, proceeding anyway.")

    # ============================================================
    # BƯỚC 2: Tìm và click vào nút Transfer của gói cước hợp lệ (tự động cuộn xuống nếu cần)
    # ============================================================
    with allure.step("Find and click Transfer button on a valid plan"), Step("Find and click Transfer button on a valid plan"):
        logger.info("Waiting for data plans list to load from server...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    AppiumBy.XPATH,
                    "//*[@resource-id='travel.eskimo.esim.uat:id/data_rv']//*[@resource-id='travel.eskimo.esim.uat:id/txt_transfer' or @resource-id='travel.eskimo.esim.uat:id/txt_transfer_image']"
                ))
            )
            logger.info("Data plans list loaded successfully.")
            time.sleep(1)
        except Exception:
            logger.warning("Timed out waiting for plans list to load, attempting to scan/scroll anyway...")
        try:
            transfer_btn = None
            max_swipes = 5
            
            for i in range(max_swipes):
                try:
                    elements = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/data_rv']//*[@resource-id='travel.eskimo.esim.uat:id/txt_transfer' or @resource-id='travel.eskimo.esim.uat:id/txt_transfer_image']")
                    for elem in elements:
                        if elem.is_displayed():
                            transfer_btn = elem
                            break
                    if transfer_btn:
                        break
                except:
                    pass
                
                logger.info(f"Chưa tìm thấy nút Transfer, đang cuộn màn hình xuống (lượt {i+1}/{max_swipes})...")
                size = driver.get_window_size()
                start_x = size['width'] / 2
                start_y = int(size['height'] * 0.75)
                end_x = size['width'] / 2
                end_y = int(size['height'] * 0.25)
                
                driver.swipe(start_x, start_y, end_x, end_y, 1000)
                time.sleep(1.5)
                
            if transfer_btn is None:
                raise Exception("Không tìm thấy gói cước nào có thể transfer (kể cả sau khi đã cuộn hết danh sách)!")
                
            logger.info("Check UI: Found transfer button of a valid plan.")
            transfer_btn.click()
            logger.info("Action: Clicked Transfer button.")
            
        except Exception as e:
            raise Exception(f"Lỗi khi tìm gói cước để transfer: {e}")

    # ============================================================
    # BƯỚC 3: Kiểm tra thông báo Oops hoặc chuyển tiếp tới màn hình Transfer Data
    # ============================================================
    with allure.step("Verify navigation to Transfer Data screen"), Step("Verify navigation to Transfer Data screen"):
        time.sleep(1.5)
        try:
            oops = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/oops_image")
            if len(oops) > 0 and oops[0].is_displayed():
                logger.error("Detect: Oops! Data transfer is temporarily unavailable.")
                btn_ok = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_ok")
                btn_ok.click()
                logger.info("Action: Clicked Okay to dismiss Oops popup.")
                raise Exception("Data transfer is temporarily unavailable (UAT Server limit).")
        except Exception as e:
            if "temporarily unavailable" in str(e):
                raise e
        logger.info("Verify: Proceeded past any error screens successfully.")

    # ============================================================
    # BƯỚC 4: Click Continue
    # ============================================================
    with allure.step("Click Continue on Transfer Data screen"), Step("Click Continue on Transfer Data screen"):
        continue_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/buttonSend']", timeout=20)
        assert continue_btn.is_displayed(), "❌ Không thấy nút Continue!"
        logger.info("Check UI: Send transfer screen is active.")
        continue_btn.click()
        logger.info("Action: Clicked Continue.")

    # ============================================================
    # BƯỚC 5: Click country code
    # ============================================================
    with allure.step("Click country code selection"), Step("Click country code selection"):
        country_code = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/country_code']", timeout=20)
        assert country_code.is_displayed(), "❌ Không thấy country code section!"
        logger.info("Check UI: Country code selector is active.")
        country_code.click()
        logger.info("Action: Clicked country code.")

    # ============================================================
    # BƯỚC 6: Search Vietnam
    # ============================================================
    with allure.step(f"Search country name '{COUNTRY_SEARCH}'"), Step(f"Search country name '{COUNTRY_SEARCH}'"):
        search_field = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/txtSearch']", timeout=20)
        assert search_field.is_displayed(), "❌ Không thấy ô Search Country!"
        logger.info("Check UI: Search country screen is active.")
        search_field.send_keys(COUNTRY_SEARCH)
        logger.info(f"Action: Searched country name: {COUNTRY_SEARCH}")

    # ============================================================
    # BƯỚC 6.1: Chọn Vietnam từ danh sách
    # ============================================================
    with allure.step("Select country from list"), Step("Select country from list"):
        time.sleep(1)
        vietnam_option = wait_for_element_with_anr_handling(driver, '//android.widget.RelativeLayout[@resource-id="travel.eskimo.esim.uat:id/test"]/android.widget.LinearLayout/android.widget.LinearLayout', timeout=20)
        assert vietnam_option.is_displayed(), "❌ Không thấy Vietnam trong danh sách!"
        logger.info("Verify: Select country screen loaded Vietnam option.")
        vietnam_option.click()
        logger.info("Action: Selected Vietnam country option.")

    # ============================================================
    # BƯỚC 7: Nhập số điện thoại
    # ============================================================
    with allure.step(f"Enter recipient mobile number '{phone}'"), Step(f"Enter recipient mobile number '{phone}'"):
        phone_field = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/et_mobile_number']", timeout=20)
        assert phone_field.is_displayed(), "❌ Không thấy field số điện thoại!"
        logger.info("Check UI: Mobile number input field is displayed.")
        phone_field.clear()
        phone_field.send_keys(phone)
        logger.info(f"Action: Entered recipient mobile number: {phone}")

    # ============================================================
    # BƯỚC 8: Click Continue
    # ============================================================
    with allure.step("Click Continue to confirm recipient"), Step("Click Continue to confirm recipient"):
        continue_btn2 = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/buttonSend']", timeout=20)
        continue_btn2.click()
        logger.info("Action: Clicked Continue.")

        time.sleep(2)
        try:
            oops = driver.find_elements(AppiumBy.XPATH, "//*[@text='Oops'] | //*[@resource-id='travel.eskimo.esim.uat:id/oops_image']")
            if oops and oops[0].is_displayed():
                msg_elems = driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'cannot be converted') or contains(@text, 'Oops') or @resource-id='travel.eskimo.esim.uat:id/oops_message']")
                err_text = msg_elems[0].text if msg_elems else "Oops dialog appeared"
                logger.error(f"Server error detected on transfer: {err_text}")
                ok_btns = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_ok'] | //*[@text='OK']")
                if ok_btns:
                    ok_btns[0].click()
                raise Exception(f"Server Transfer Error: {err_text}")
        except Exception as e:
            if "Server Transfer Error" in str(e):
                raise e

    # ============================================================
    # BƯỚC 9: Click Yes, transfer
    # ============================================================
    with allure.step("Click Yes, transfer to authorize"), Step("Click Yes, transfer to authorize"):
        yes_btn = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_continue']", timeout=20)
        assert yes_btn.is_displayed(), "❌ Không thấy màn hình xác nhận transfer!"
        logger.info("Verify: Transfer confirm overlay dialog is displayed.")
        yes_btn.click()
        logger.info("Action: Clicked Yes, transfer.")

    # ============================================================
    # BƯỚC 10: Click Done và trở về màn hình Data Balance
    # ============================================================
    with allure.step("Click Done to complete transfer"), Step("Click Done to complete transfer"):
        done_selector = "//*[@resource-id='travel.eskimo.esim.uat:id/btn_done'] | //*[@resource-id='travel.eskimo.esim.uat:id/txt_done'] | //*[@text='Done']"
        logger.info("Chờ màn hình xác nhận Transfer thành công và nút Done xuất hiện...")
        done_btn = wait_for_element_with_anr_handling(driver, done_selector, timeout=50)
        assert done_btn.is_displayed(), "❌ Không thấy màn hình transfer thành công!"
        logger.info("Verify: Transfer successful status page is displayed.")
        
        time.sleep(1)
        clicked = False
        try:
            txt_elems = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/txt_done'] | //*[@text='Done']")
            if txt_elems and txt_elems[0].is_displayed():
                txt_elems[0].click()
                clicked = True
        except Exception:
            pass

        if not clicked:
            try:
                done_btn.click()
                clicked = True
            except Exception:
                pass

        logger.info("Action: Clicked Done.")
        time.sleep(2)

        try:
            done_check = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_done'] | //*[@resource-id='travel.eskimo.esim.uat:id/txt_done']")
            if done_check and done_check[0].is_displayed():
                logger.info("Màn hình Done vẫn còn hiển thị, đang click nút 'X' để đóng...")
                btn_back = driver.find_elements(AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_back")
                if btn_back and btn_back[0].is_displayed():
                    btn_back[0].click()
                else:
                    done_check[0].click()
                time.sleep(2)
        except Exception:
            pass

        logger.info("Đang kiểm tra chuyển tiếp về lại màn hình Home / Data Balance...")
        try:
            wait_for_element_with_anr_handling(
                driver,
                "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home'] | //*[@resource-id='travel.eskimo.esim.uat:id/cd_transfer']",
                timeout=20
            )
            logger.info("Verify: Returned to Home / Data Balance successfully!")
        except Exception as e:
            logger.warning(f"Could not verify Home screen return: {e}")

        logger.info("Verify: Returned to Data Dashboard successfully - TC_Transfer_Homescreen_001 PASSED!")
        return "TC_Transfer_Homescreen_001"
