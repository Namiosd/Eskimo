from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time

desired_caps = {
    "platformName": "Android",
    "deviceName": "emulator-5554",
    "automationName": "UiAutomator2",
    "noReset": True,
    "uiautomator2ServerLaunchTimeout": 60000,
    "uiautomator2ServerInstallTimeout": 60000,
}

from selenium.webdriver.common.options import ArgOptions

class AppiumOptions(ArgOptions):
    @property
    def default_capabilities(self):
        return {}

options = AppiumOptions()
for k, v in desired_caps.items():
    options.set_capability(k, v)

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

print("✅ Kết nối emulator thành công!")
time.sleep(3)

driver.quit()
print("✅ Test hoàn thành!")