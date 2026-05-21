import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper_login import create_driver, login
import time

driver = create_driver()

try:
    login(driver)
    print("\n🎉 TC_LOGIN_HOME — PASSED!")

except Exception as e:
    print(f"\n❌ TC_LOGIN_HOME — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
