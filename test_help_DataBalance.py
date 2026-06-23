from helper_login import create_driver
from helper_help import click_help
import time

driver = create_driver()

try:
    # Precondition: đã login, đang ở màn hình Data Dashboard
    time.sleep(3)

    # BƯỚC 1: Click Help từ Data Dashboard
    click_help(driver)

    print("\n🎉 TC_HELP_001 — PASSED!")

except Exception as e:
    print(f"\n❌ TC_HELP_001 — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
