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
    try:
        with open("page_source.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Saved page source to page_source.xml")
    except Exception as pe:
        print(f"Could not save page source: {pe}")

finally:
    time.sleep(3)
    driver.quit()
    print("✅ Đã đóng session")
