from helper_login import create_driver, login
from helper_transfer import transfer_data
import time

driver = create_driver()

try:
    login(driver)
    print("\n✅ Login thành công — bắt đầu test Transfer")

    result = transfer_data(driver)
    print(f"\n🎉 Test Transfer — {result} PASSED!")

except Exception as e:
    print(f"\n❌ Test Transfer — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
