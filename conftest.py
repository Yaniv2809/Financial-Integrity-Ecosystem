from playwright.sync_api import Playwright
import pytest
from utils.logger import Logger
import os
import time
from extensions.db_actions import DBActions
from config.config import ConfigManager

# ==========================================
# Global Paths
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "reports", "screenshots")
TRACES_DIR = os.path.join(PROJECT_ROOT, "reports", "traces")

# יצירת תיקיות דוחות אם לא קיימות
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(TRACES_DIR, exist_ok=True)


# ==========================================
# 0. General - Setup/Teardown + Logging
# ==========================================
@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    log = Logger()
    log.info("====== SETUP: Starting Test Execution ======")
    yield
    log.info("====== TEARDOWN: Test Execution Completed ======")


# ==========================================
# 1. DB Fixtures - Session scope
# ==========================================
@pytest.fixture(scope="session")
def db_setup_teardown():
    """
    יוצר את טבלת expenses אם אינה קיימת, ומנקה נתוני טסט בסיום.
    שימו לב: לא autouse - רק טסטים שצריכים DB ישתמשו בזה.
    ב-test_db.py יש להשתמש ב: @pytest.mark.usefixtures("db_setup_teardown")
    """
    print("\n[SETUP] Initializing Global DB Environment...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        expense_name TEXT, 
        amount REAL, 
        date TEXT, 
        category TEXT
    )"""
    DBActions.execute_query(DB_PATH, create_table_query)
    yield
    print("\n[TEARDOWN] Cleaning up Global DB Environment...")
    DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name LIKE '%Test%'")


# ==========================================
# 2. Web Fixtures (Playwright) 
# ==========================================
@pytest.fixture(scope="class")
def web_setup(request, playwright: Playwright):
    print("\n[SETUP] Launching Chrome Browser...")
    browser = playwright.chromium.launch(headless=False, channel="chrome", slow_mo=1000)
    context = browser.new_context()
    page = context.new_page()
    url = ConfigManager.get_env_data()['web_url']
    page.goto(url)
    
    request.cls.page = page
    request.cls.context = context
    
    yield
    
    print("\n[TEARDOWN] Closing Browser...")
    page.close()
    context.close()
    browser.close()

@pytest.fixture(scope="function", autouse=True)
def trace_manager(request):
    """ מנהל את ה-Tracing פר טסט כדי שלא יעצור לשאר המחלקה """
    if hasattr(request.cls, "context") and request.cls.context is not None:
        # מתחילים הקלטה לטסט הנוכחי
        request.cls.context.tracing.start(screenshots=True, snapshots=True)
        
    yield # כאן הטסט רץ 
    
    # ה-Hook של הכישלון ישמור את הקובץ אם נכשל, אבל כאן נוודא שההקלטה נעצרת בכל מקרה
    # כדי שהטסט הבא יוכל להתחיל הקלטה נקייה.
    if hasattr(request.cls, "context") and request.cls.context is not None:
        try:
            # עוצרים בלי לשמור (השמירה קורית ב-Hook אם יש כישלון)
            request.cls.context.tracing.stop() 
        except:  # noqa: E722
            pass


# ==========================================
# 3. API Fixtures - Function scope
# ==========================================
@pytest.fixture(scope="function")
def api_setup():
    """
    פיקסטור לטסטים של API.
    ה-URL מוגדר ב-Workflows, כאן ניתן להוסיף Token/Auth בעתיד.
    """
    print("\n[SETUP] Preparing API Environment...")
    yield
    print("\n[TEARDOWN] API Test Completed.")


# ==========================================
# 4. Mobile Fixtures (Appium) - Class scope
# ==========================================
@pytest.fixture(scope="class")
def mobile_driver(request):
    import os
    from appium import webdriver as appium_webdriver
    from appium.options.android import UiAutomator2Options
    from data.mobile.mobile import MOBILE_CAPS, APPIUM_SERVER, TIMEOUT

    # ---------------------------------------------------------
    # זריקת משתנה הסביבה ישירות לתוך התהליך כדי לעקוף את ווינדוס
    # ---------------------------------------------------------
    android_sdk_path = r"C:\Users\yaniv\AppData\Local\Android\Sdk"
    os.environ["ANDROID_HOME"] = android_sdk_path
    os.environ["ANDROID_SDK_ROOT"] = android_sdk_path

    print("\n[SETUP] Launching Official Appium Server Driver...")
    
    # טעינת ההגדרות דרך המחלקה הרשמית של אנדרואיד (UiAutomator2Options)
    options = UiAutomator2Options().load_capabilities(MOBILE_CAPS)
    
    driver = appium_webdriver.Remote(APPIUM_SERVER, options=options)
    driver.implicitly_wait(TIMEOUT)
    # שיתוף ה-driver עם מחלקת הטסטים
    request.cls.driver = driver

    yield driver

    print("\n[TEARDOWN] Closing Appium Driver...")
    driver.quit()

# ==========================================
# 5. Screenshot & Trace on Failure
# ==========================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook שרץ אחרי כל טסט.
    אם הטסט נכשל - שומר screenshot (web/mobile) ו-trace (web).
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        test_name = item.name
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}"

        # Web screenshot + trace
        if hasattr(item.cls, "page") and item.cls.page is not None:
            try:
                page = item.cls.page
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"{filename}.png"))
                print(f"\n[FAILURE] Web screenshot saved: {filename}.png")
            except Exception as e:
                print(f"\n[WARNING] Failed to capture web screenshot: {e}")

            # שמירת Trace
            if hasattr(item.cls, "context") and item.cls.context is not None:
                try:
                    item.cls.context.tracing.stop(path=os.path.join(TRACES_DIR, f"{filename}.zip"))
                    print(f"[FAILURE] Trace saved: {filename}.zip")
                except Exception as e:
                    print(f"[WARNING] Failed to save trace: {e}")

        # Mobile screenshot
        elif hasattr(item.cls, "driver") and item.cls.driver is not None:
            try:
                driver = item.cls.driver
                driver.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"{filename}_mobile.png"))
                print(f"\n[FAILURE] Mobile screenshot saved: {filename}_mobile.png")
            except Exception as e:
                print(f"\n[WARNING] Failed to capture mobile screenshot: {e}")
