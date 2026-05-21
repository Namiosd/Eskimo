from helper_login import create_driver, login
from helper_redeem import redeem_voucher
import time

VOUCHER_CODE = "1-VNXNAAZCO"

driver = create_driver()

try:
    login(driver)
    print("\n✅ Login thành công — bắt đầu test Redeem")

    result = redeem_voucher(driver, VOUCHER_CODE)
    print(f"\n🎉 Test Redeem — {result} PASSED!")

except Exception as e:
    print(f"\n❌ Test Redeem — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
