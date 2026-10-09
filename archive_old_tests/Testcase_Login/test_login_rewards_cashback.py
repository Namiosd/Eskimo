import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper_login import create_driver, login_from_rewards_cashback
import time

driver = create_driver()

try:
    login_from_rewards_cashback(driver)
    print("\n🎉 TC_LOGIN_REWARDS_CASHBACK — PASSED!")

except Exception as e:
    print(f"\n❌ TC_LOGIN_REWARDS_CASHBACK — FAILED: {e}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
