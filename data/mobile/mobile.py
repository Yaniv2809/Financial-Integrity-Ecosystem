# Appium capabilities for Android device (Atid Expense Tracker app)
MOBILE_CAPS = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:udid": "jb4xaa45q4jzinjf",
    # Using the pre-installed app package instead of APK file path
    "appium:appPackage": "com.atidcollege.atidexpensetracker",
    "appium:appActivity": ".MainActivity",
    "appium:autoGrantPermissions": True
}

APPIUM_SERVER = "http://127.0.0.1:4723"
TIMEOUT = 10
