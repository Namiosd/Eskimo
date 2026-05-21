import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper_login import create_driver, login_from_account
import time

driver = create_driver()

try:
    login_from_account(driver)
    print("\n🎉 TC_LOGIN_ACCOUNT — PASSED!")

except Exception as e:
    print(f"\n❌ TC_LOGIN_ACCOUNT — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
