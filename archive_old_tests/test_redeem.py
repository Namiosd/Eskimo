from helper_login import create_driver, login
from helper_redeem import redeem_voucher
import time

# 1. Đọc tất cả các dòng voucher, bỏ qua dòng trống
with open("voucher_code.txt", "r") as f:
    VOUCHER_CODES = [line.strip() for line in f if line.strip()]

driver = create_driver()

try:
    login(driver)
    print("\n✅ Login thành công — bắt đầu test Redeem")

    # 2. Chạy vòng lặp qua từng Voucher Code
    for code in VOUCHER_CODES:
        print(f"\n--- Đang test với Voucher: {code} ---")
        try:
            result = redeem_voucher(driver, code)
            print(f"🎉 Test Redeem {code} — {result} PASSED!")
        except Exception as inner_e:
            print(f"❌ Test Redeem {code} — FAILED: {inner_e}")

except Exception as e:
    print(f"\n❌ Lỗi hệ thống: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")

