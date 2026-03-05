from playwright.sync_api import Playwright
import pytest
import os
import time
import allure
from extensions.db_actions import DBActions
from config.config import ConfigManager
from workflows.api.api_workflows_expense import APIWorkflows
from utils.ai import get_ai_error_analysis 

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
# @pytest.fixture(scope="function", autouse=True)
# def setup_teardown():
#     log = Logger()
#     log.info("====== SETUP: Starting Test Execution ======")
#     yield
#     log.info("====== TEARDOWN: Test Execution Completed ======")


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
    # 1. קביעת מהירות ברירת המחדל (איטי לטובת שאר הטסטים)
    slow_mo_value = 1000
    # 2. בדיקה חכמה: האם הטסט או המחלקה קיבלו תווית של ריצה מהירה?
    if request.node.get_closest_marker("fast_browser"):
        slow_mo_value = 0  # ביטול ההשהיה לטובת בדיקות ביצועים
    print(f"\n[SETUP] Launching Chrome Browser (slow_mo={slow_mo_value})...")
    # 3. הפעלת הדפדפן עם המהירות הדינמית
    browser = playwright.chromium.launch(headless=False, channel="chrome", slow_mo=slow_mo_value)
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
        except Exception as e:
            # תופס רק שגיאות קוד אמיתיות ולא חוסם עצירת מערכת (כמו Ctrl+C)
            print(f"[TRACE CLEANUP WARNING] Could not stop tracing: {e}")


# ==========================================
# 3. API Fixtures - Function scope
# ==========================================
# @pytest.fixture(scope="function")
# def api_setup():
#     """
#     פיקסטור לטסטים של API.
#     ה-URL מוגדר ב-Workflows, כאן ניתן להוסיף Token/Auth בעתיד.
#     """
#     print("\n[SETUP] Preparing API Environment...")
#     yield
#     print("\n[TEARDOWN] API Test Completed.")

@pytest.fixture(scope="function")
def api_cleanup():
    """
    פיקסטור לניקוי נתונים שנוצרו במהלך טסטי API.
    יש להשתמש בזה בטסטים שיוצרים נתונים (POST/PUT) כדי לשמור על סביבה נקייה.
    ב-test_api.py יש להשתמש ב: @pytest.mark.usefixtures("api_cleanup")
    """
    yield
    print("\n[TEARDOWN] Cleaning up API Test Data...")
    # כאן ניתן להוסיף לוגיקה לניקוי נתונים שנוצרו במהלך הטסט, למשל מחיקת הוצאות שנוצרו.

@pytest.fixture(scope="function")
def api_token():
    """
    פיקסטור לקבלת Token לאימות בבקשות API.
    כרגע מחזיר ערך סטטי, אבל ניתן להרחיב בעתיד לקבלת Token דינמי מהשרת.
    """
    # כאן ניתן להוסיף לוגיקה לקבלת Token אמיתי מהשרת אם יש צורך
    return "Bearer dummy_token_for_testing"

@pytest.fixture(scope="function")
def temp_expense_id():
    """
    פיקסטור ליצירת הוצאה זמנית לפני טסט ולקבל את ה-ID שלה.
    לאחר הטסט, ניתן למחוק את ההוצאה כדי לשמור על סביבה נקייה.
    """
    # יצירת הוצאה זמנית
    response = APIWorkflows.create_expense("Temp_Expense", 999, "2025-12-31", "Testing")
    expense_id = response.json().get("id")
    yield expense_id
    # ניקוי - מחיקת ההוצאה הזמנית
    APIWorkflows.delete_expense(expense_id)


@pytest.fixture(scope="function")
def smart_expense_id():
    from tests.api.test_api_expense import TestAPI

    if TestAPI.created_id is not None:
        # ריצת מחלקה - test02 כבר יצר את ההוצאה
        yield TestAPI.created_id
        # אין cleanup - test06 ידאג למחיקה
    else:
        # ריצה עצמאית - יוצר הוצאה זמנית עם cleanup אוטומטי
        response = APIWorkflows.create_expense("Temp_Expense", 999, "2025-12-31", "Testing")
        temp_id = response.json().get("id")
        yield temp_id
        APIWorkflows.delete_expense(temp_id)  # cleanup רק בריצה עצמאית



# ==========================================
# 4. Mobile Fixtures (Appium) - Class scope
# ==========================================
@pytest.fixture(scope="class")
def mobile_driver(request):
    from appium import webdriver as appium_webdriver
    from appium.options.android import UiAutomator2Options
    from data.mobile.mobile import MOBILE_CAPS, APPIUM_SERVER, TIMEOUT

    ConfigManager.get_env_data()['android_sdk_path']

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
# 5. Screenshot & Trace on Failure & AI
# ==========================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        test_name = item.name
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}"

        # 1. Web screenshot + trace (הקוד המקורי והטוב שלך)
        if hasattr(item.cls, "page") and item.cls.page is not None:
            try:
                page = item.cls.page
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"{filename}.png"))
                print(f"\n[FAILURE] Web screenshot saved: {filename}.png")
            except Exception as e:
                print(f"\n[WARNING] Failed to capture web screenshot: {e}")

            if hasattr(item.cls, "context") and item.cls.context is not None:
                try:
                    item.cls.context.tracing.stop(path=os.path.join(TRACES_DIR, f"{filename}.zip"))
                    print(f"[FAILURE] Trace saved: {filename}.zip")
                except Exception as e:
                    print(f"[WARNING] Failed to save trace: {e}")

        # 2. Mobile screenshot (הקוד המקורי שלך)
        elif hasattr(item.cls, "driver") and item.cls.driver is not None:
            try:
                driver = item.cls.driver
                driver.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"{filename}_mobile.png"))
                print(f"\n[FAILURE] Mobile screenshot saved: {filename}_mobile.png")
            except Exception as e:
                print(f"\n[WARNING] Failed to capture mobile screenshot: {e}")

        # ==========================================
        # 3. AI 🤖
        # ==========================================
        # בודק אם המשתמש ביקש להפעיל את ה-AI בהרצה הזו
        # בודק האם לטסט הספציפי הזה יש את המרקר שלנו
        if item.get_closest_marker("use_ai"):
            error_message = str(call.excinfo.value) if call.excinfo else "Unknown error"
            print(f"\n[AI Analysis] Analyzing failure in {test_name}... please wait...")
            
            try:
                ai_explanation = get_ai_error_analysis(error_message)
                
                print("\n============= AI ERROR ANALYSIS =============")
                print(ai_explanation)
                print("=============================================\n")
                
                # הצמדה לדוח האליור
                allure.attach(
                    body=f" Error Message:\n{error_message}\n\n🤖 AI Analysis:\n{ai_explanation}", 
                    name="🤖 AI Failure Analysis", 
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                print(f"[WARNING] AI Analysis failed to execute: {e}")


def pytest_addoption(parser):
    """מוסיף דגל מותאם אישית להרצת AI על שגיאות"""
    parser.addoption(
        "--ai-analysis", action="store_true", default=False, help="Run AI analysis on test failures"
    )
