from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def buy_data_plan(driver, plan_name="Global", data_size="1 GB"):
    wait = WebDriverWait(driver, 30)  # tăng timeout lên 30s

    # Chờ app load xong sau login
    time.sleep(5)
    driver.save_screenshot("D:\\ESKIMO\\debug_step0.png")
    print("✅ [Debug] Screenshot step0 — mở D:\\ESKIMO\\debug_step0.png xem app đang ở màn hình nào")

    # ============================================================
    # BƯỚC 1: Click vào gói Global trên màn hình Home
    # ============================================================
    global_plan = wait.until(
        EC.element_to_be_clickable((AppiumBy.XPATH, '//androidx.cardview.widget.CardView[@resource-id="travel.eskimo.esim.uat:id/global_section"]/android.view.ViewGroup'))
    )
    assert global_plan.is_displayed(), f"❌ Không thấy gói {plan_name}!"
    print(f"✅ [Check UI] Gói {plan_name} hiển thị đúng")

    global_plan.click()
    print(f"✅ [Action] Đã click vào gói {plan_name}")

    plan_list = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/recyclerView"))
    )
    assert plan_list.is_displayed(), "❌ Không thấy danh sách data plan!"
    print("✅ [Verify] Danh sách data plan hiển thị đúng")

    # ============================================================
    # BƯỚC 2: Chọn gói 21 GB (card đầu tiên)
    # ============================================================
    plan_item = wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="travel.eskimo.esim.uat:id/recyclerView"]/androidx.cardview.widget.CardView[1]/android.widget.LinearLayout'))
    )
    assert plan_item.is_displayed(), f"❌ Không thấy gói {data_size}!"
    print(f"✅ [Check UI] Gói {data_size} hiển thị đúng")

    plan_item.click()
    print(f"✅ [Action] Đã chọn gói {data_size}")

    buy_now_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_buy_now"))
    )
    assert buy_now_btn.is_displayed(), "❌ Không thấy nút Buy now!"
    print("✅ [Verify] Nút Buy now hiển thị đúng")

    # ============================================================
    # BƯỚC 3: Click Buy now
    # ============================================================
    buy_now_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_buy_now"))
    )
    assert buy_now_btn.is_displayed(), "❌ Không thấy nút Buy now!"
    print("✅ [Check UI] Nút Buy now hiển thị đúng")

    buy_now_btn.click()
    print("✅ [Action] Đã click Buy now")

    time.sleep(3)
    continue_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_continue"))
        
    )
    assert continue_btn.is_displayed(), "❌ Không thấy popup Buy Now Use Later!"
    print("✅ [Verify] Popup Buy Now Use Later hiển thị đúng")

    # ============================================================
    # BƯỚC 4: Click Continue trên popup
    # ============================================================
    assert continue_btn.is_displayed(), "❌ Không thấy nút Continue!"
    print("✅ [Check UI] Nút Continue hiển thị đúng")

    continue_btn.click()
    print("✅ [Action] Đã click Continue")

    time.sleep(3)
    driver.save_screenshot("D:\\ESKIMO\\debug_step4.png")
    print("✅ [Debug] Screenshot step4 — xem màn hình sau Continue popup")

    checkout_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/checkout"))
    )
    assert checkout_btn.is_displayed(), "❌ Không thấy màn hình Checkout!"
    print("✅ [Verify] Màn hình Checkout hiển thị đúng")

    # ============================================================
    # BƯỚC 5: Click Continue to payment
    # ============================================================
    assert checkout_btn.is_displayed(), "❌ Không thấy nút Continue to payment!"
    print("✅ [Check UI] Nút Continue to payment hiển thị đúng")

    checkout_btn.click()
    print("✅ [Action] Đã click Continue to payment")

    time.sleep(3)
    pay_by_card = wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="travel.eskimo.esim.uat:id/container_card_methods"]/androidx.cardview.widget.CardView/android.view.ViewGroup'))
    )
    assert pay_by_card.is_displayed(), "❌ Không thấy màn hình Payment method!"
    print("✅ [Verify] Màn hình Payment method hiển thị đúng")

    # ============================================================
    # BƯỚC 6: Chọn Pay by Card
    # ============================================================
    assert pay_by_card.is_displayed(), "❌ Không thấy nút Pay by Card!"
    print("✅ [Check UI] Pay by Card hiển thị đúng")

    pay_by_card.click()
    print("✅ [Action] Đã chọn Pay by Card")

    # ============================================================
    # BƯỚC 7: Click Continue (Payment method)
    # ============================================================
    payment_continue = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/checkout"))
    )
    assert payment_continue.is_displayed(), "❌ Không thấy nút Continue!"
    print("✅ [Check UI] Nút Continue hiển thị đúng")

    payment_continue.click()
    print("✅ [Action] Đã click Continue")

    time.sleep(3)
    pay_btn = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/primary_button"))
    )
    assert pay_btn.is_displayed(), "❌ Không thấy màn hình Stripe Payment!"
    print("✅ [Verify] Màn hình Stripe Payment hiển thị đúng")

    # ============================================================
    # BƯỚC 8: Click Pay
    # ============================================================
    assert pay_btn.is_displayed(), "❌ Không thấy nút Pay!"
    print("✅ [Check UI] Nút Pay hiển thị đúng")

    pay_btn.click()
    print("✅ [Action] Đã click Pay")

    time.sleep(5)
    success_msg = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/payment_status_message"))
    )
    assert success_msg.is_displayed(), "❌ Không thấy màn hình thanh toán thành công!"
    print(f"✅ [Verify] Thanh toán thành công — {success_msg.text}")

    # ============================================================
    # BƯỚC 9: Click See my data
    # ============================================================
    see_data_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ID, "travel.eskimo.esim.uat:id/btn_ok"))
    )
    assert see_data_btn.is_displayed(), "❌ Không thấy nút See my data!"
    print("✅ [Check UI] Nút See my data hiển thị đúng")

    see_data_btn.click()
    print("✅ [Action] Đã click See my data")

    time.sleep(3)
    my_plans_tab = wait.until(
        EC.presence_of_element_located((AppiumBy.ID, "travel.eskimo.esim.uat:id/txt_my_plan"))
    )
    assert my_plans_tab.is_displayed(), "❌ Không thấy màn hình My Plans!"
    print("✅ [Verify] Màn hình My Plans hiển thị — Mua data plan thành công!")
