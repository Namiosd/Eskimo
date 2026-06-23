from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper_redeem import navigate_to_home
import time

PHONE_NUMBER = "372217316"
COUNTRY_SEARCH = "Vietnam"


def transfer_data(driver, phone=PHONE_NUMBER):
    """
    TC_Transfer_Homescreen_001: Transfer data plan cho người khác.
    Precondition: Đã login, đang ở bất kỳ màn hình nào.
    """
    wait = WebDriverWait(driver, 20)

    # Navigate về Home trước
    navigate_to_home(driver)

    # ============================================================
    # BƯỚC 1: Click Transfer data to anyone section
    # ============================================================
    transfer_card = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/transfer_card"))
    )
    assert transfer_card.is_displayed(), "❌ Không thấy Transfer card!"
    print("✅ [Check UI] Transfer card hiển thị")
    transfer_card.click()
    print("✅ [Action] Đã click Transfer data to anyone section")

    # ============================================================
    # BƯỚC 2: Tìm và click vào nút Transfer của gói cước hợp lệ (tự động cuộn xuống nếu cần)
    # ============================================================
    time.sleep(2)  # Chờ danh sách gói cước tải xong
    try:
        transfer_btn = None
        max_swipes = 5
        
        for i in range(max_swipes):
            try:
                # Kiểm tra xem nút Transfer có xuất hiện chưa
                btn = driver.find_element(AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_transfer_image")
                if btn.is_displayed():
                    transfer_btn = btn
                    break
            except:
                pass
            
            # Nếu chưa thấy, thực hiện vuốt từ dưới lên trên (cuộn màn hình xuống)
            print(f"ℹ️ Chưa tìm thấy nút Transfer, đang cuộn màn hình xuống (lượt {i+1}/{max_swipes})...")
            size = driver.get_window_size()
            start_x = size['width'] / 2
            start_y = int(size['height'] * 0.75)  # Vuốt từ dưới (75% chiều cao)
            end_x = size['width'] / 2
            end_y = int(size['height'] * 0.25)    # Lên trên (25% chiều cao)
            
            driver.swipe(start_x, start_y, end_x, end_y, 1000)
            time.sleep(1.5)  # Đợi danh sách cuộn xong ổn định
            
        if transfer_btn is None:
            raise Exception("Không tìm thấy gói cước nào có thể transfer (kể cả sau khi đã cuộn hết danh sách)!")
            
        print("✅ [Check UI] Đã tìm thấy gói cước có thể transfer")
        transfer_btn.click()
        print("✅ [Action] Đã click nút Transfer của gói cước")
        
    except Exception as e:
        raise Exception(f"Lỗi khi tìm gói cước để transfer: {e}")

    # ============================================================
    # BƯỚC 3: Click Transfer icon → vào màn hình Transfer Data
    # ============================================================
    transfer_icon = wait.until(
        EC.element_to_be_clickable((AppiumBy.XPATH,
            "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout"))
    )
    assert transfer_icon.is_displayed(), "❌ Không thấy Transfer icon!"
    print("✅ [Check UI] Màn hình Transfer Data hiển thị")
    transfer_icon.click()
    print("✅ [Action] Đã click Transfer icon")

    # ============================================================
    # BƯỚC 4: Click Continue
    # ============================================================
    continue_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/buttonSend"))
    )
    assert continue_btn.is_displayed(), "❌ Không thấy nút Continue!"
    print("✅ [Check UI] Màn hình transfer data hiển thị")
    continue_btn.click()
    print("✅ [Action] Đã click Continue")

    # ============================================================
    # BƯỚC 5: Click country code
    # ============================================================
    country_code = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/country_code"))
    )
    assert country_code.is_displayed(), "❌ Không thấy country code section!"
    print("✅ [Check UI] Country code section hiển thị")
    country_code.click()
    print("✅ [Action] Đã click country code")

    # ============================================================
    # BƯỚC 6: Search Vietnam
    # ============================================================
    search_field = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txtSearch"))
    )
    assert search_field.is_displayed(), "❌ Không thấy ô Search Country!"
    print("✅ [Check UI] Màn hình Country code hiển thị")
    search_field.send_keys(COUNTRY_SEARCH)
    print(f"✅ [Action] Đã nhập '{COUNTRY_SEARCH}' vào ô search")

    # ============================================================
    # BƯỚC 6.1: Chọn Vietnam từ danh sách
    # ============================================================
    time.sleep(1)
    vietnam_option = wait.until(
        EC.element_to_be_clickable((AppiumBy.XPATH,
            '//android.widget.RelativeLayout[@resource-id="travel.eskimo.esim.uat:id/test"]/android.widget.LinearLayout/android.widget.LinearLayout'))
    )
    assert vietnam_option.is_displayed(), "❌ Không thấy Vietnam trong danh sách!"
    print("✅ [Verify] Màn hình chọn Vietnam hiển thị")
    vietnam_option.click()
    print("✅ [Action] Đã chọn Vietnam")

    # ============================================================
    # BƯỚC 7: Nhập số điện thoại
    # ============================================================
    phone_field = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/et_mobile_number"))
    )
    assert phone_field.is_displayed(), "❌ Không thấy field số điện thoại!"
    print("✅ [Check UI] Field số điện thoại hiển thị")
    phone_field.clear()
    phone_field.send_keys(phone)
    print(f"✅ [Action] Đã nhập số điện thoại: {phone}")

    # ============================================================
    # BƯỚC 8: Click Continue
    # ============================================================
    continue_btn2 = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/buttonSend"))
    )
    continue_btn2.click()
    print("✅ [Action] Đã click Continue")

    # ============================================================
    # BƯỚC 9: Click Yes, transfer
    # ============================================================
    yes_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_continue"))
    )
    assert yes_btn.is_displayed(), "❌ Không thấy màn hình xác nhận transfer!"
    print("✅ [Verify] Màn hình hỏi transfer hiển thị")
    yes_btn.click()
    print("✅ [Action] Đã click Yes, transfer")

    # ============================================================
    # BƯỚC 10: Click Done
    # ============================================================
    done_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_done"))
    )
    assert done_btn.is_displayed(), "❌ Không thấy màn hình transfer thành công!"
    print("✅ [Verify] Transfer thành công — màn hình Done hiển thị")
    done_btn.click()
    print("✅ [Action] Đã click Done — về lại màn hình Data Dashboard")

    print("✅ TC_Transfer_Homescreen_001 PASSED! ✅")
    return "TC_Transfer_Homescreen_001"
