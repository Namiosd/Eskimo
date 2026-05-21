from helper_login import create_driver
from helper_buy_data import buy_data_plan
import time

# Kết nối emulator
driver = create_driver()

try:
    # App đang ở Home (noReset=true) — không cần login lại
    time.sleep(3)

    # Mua data plan
    buy_data_plan(driver)

    print("\n🎉 Test Buy Data Plan — PASSED!")

except Exception as e:
    print(f"\n❌ Test Buy Data Plan — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")