from helper_login import create_driver, login #"Lấy 2 công cụ từ file helper_login.py ra dùng"  # create_driver = công cụ kết nối emulator #login = công cụ thực hiện các bước login
import time

driver = create_driver() #"Kết nối vào emulator, lưu kết nối đó vào biến driver"

#"Thử thực hiện login"
try:   #try = thử làm, nếu có lỗi thì không crash ngay
    login(driver) #login(driver) = chạy toàn bộ các bước login trong helper_login.py
    print("\n🎉 Test Login — PASSED!") 

#"Nếu có lỗi xảy ra thì in ra lỗi đó"
except Exception as e:
    print(f"\n❌ Test Login — FAILED: {e}")

#"Dù thành công hay thất bại, đợi 3 giây rồi đóng kết nối"
finally:
    time.sleep(3)
    driver.quit() #driver.quit() = đóng session, giải phóng emulator
    print("✅ Đã đóng session")
