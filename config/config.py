from typing import Dict, Any


class TestConfig:
    """Centralized configuration for Eskimo eSIM UAT test automation."""
    
    APPIUM_URL: str = "http://127.0.0.1:4723"
    PHONE_NUMBER: str = "372217312"
    OTP: str = "1234"
    COUNTRY_SEARCH: str = "Vietnam"
    APP_PACKAGE: str = "travel.eskimo.esim.uat"
    APP_ACTIVITY: str = "com.hotspot.travel.hotspot.activity.PreLoaderActivity"
    DEVICE_NAME: str = "emulator-5554"
    PLATFORM_NAME: str = "Android"
    AUTOMATION_NAME: str = "UiAutomator2"

    @classmethod
    def get_desired_capabilities(cls) -> Dict[str, Any]:
        """Generate desired capabilities for Appium Remote Session connection."""
        return {
            "platformName": cls.PLATFORM_NAME,
            "deviceName": cls.DEVICE_NAME,
            "automationName": cls.AUTOMATION_NAME,
            "appPackage": cls.APP_PACKAGE,
            "appActivity": cls.APP_ACTIVITY,
            "appWaitActivity": "*",
            "noReset": True,  # Keep the app logged in session across runs
            "uiautomator2ServerLaunchTimeout": 60000,
            "uiautomator2ServerInstallTimeout": 60000,
            "adbExecTimeout": 60000,
            "skipUnlock": True,
            "keepAlive": True,
            "newCommandTimeout": 120,
        }
