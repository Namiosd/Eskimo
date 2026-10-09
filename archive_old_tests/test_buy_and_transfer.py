from helper_login import create_driver, login
from helper_buy_data import buy_data_plan
from helper_transfer import transfer_data
import time

# Kết nối emulator
driver = create_driver()

try:
    # Bước 1: Login
    print("\n[STEP 1] Đang thực hiện đăng nhập...")
    login(driver)
    print("✅ Đăng nhập thành công (hoặc đã đăng nhập sẵn)!")

    # Bước 2: Buy Data
    print("\n[STEP 2] Đang thực hiện mua gói data...")
    buy_data_plan(driver)
    print("✅ Mua gói data thành công!")

    # Bước 3: Transfer Data
    print("\n[STEP 3] Đang thực hiện chuyển dữ liệu (transfer data)...")
    result = transfer_data(driver)
    print(f"✅ Chuyển dữ liệu thành công: {result}!")

    print("\n🎉 Toàn bộ quy trình Test Buy -> Transfer đã hoàn thành thành công (PASSED)!")

except Exception as e:
    print(f"\n❌ Test thất bại tại bước gặp lỗi: {e}")
    try:
        with open("page_source.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Đã lưu page source vào page_source.xml để debug")
    except Exception as pe:
        print(f"Không thể lưu page source: {pe}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng Appium session")
