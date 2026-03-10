from playwright.sync_api import Playwright
import pytest
import os
import time
import allure
import requests
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
LOGS_DIR = os.path.join(PROJECT_ROOT, "reports", "logs")

# # יצירת תיקיות דוחות אם לא קיימות
# os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
# os.makedirs(TRACES_DIR, exist_ok=True)
# os.makedirs(LOGS_DIR, exist_ok=True)


# ==========================================
# 1. DB Fixtures - Session scope
# ==========================================

@pytest.fixture(scope="function")
def inject_web_course_record():
    """מזריק רשומת Web_Course ל-DB לטסטי DB→Web integration"""
    db_path = ConfigManager.get_db_path()
    
    print("\n[SETUP] Injecting 'Web_Course' record into DB...")
    DBActions.execute_query(db_path, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")
    
    insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
    DBActions.execute_query(db_path, insert_query, ("Web_Course", 1500.0, "2026-02-25", "Education"))
    
    yield
    
    print("\n[TEARDOWN] Keeping DB record for inspection.")

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
        request.cls._trace_saved = False  # דגל: האם ה-Hook כבר שמר את ה-trace?
        request.cls.context.tracing.start(screenshots=True, snapshots=True)

    yield  # כאן הטסט רץ

    # עוצרים רק אם ה-Hook לא כבר עצר ושמר (בנפילה) - מונע double-stop
    if hasattr(request.cls, "context") and request.cls.context is not None:
        if not getattr(request.cls, "_trace_saved", False):
            request.cls.context.tracing.stop()  # הטסט עבר - עוצרים ללא שמירה


# ==========================================
# 3. API Fixtures - Function scope
# ==========================================
@pytest.fixture(scope="function")
def api_setup(request):
    """
    פיקסטור לטסטים של API.
    מגדיר סשן (Session) לביצועים מהירים, כותרות דיפולטיביות, וכתובת בסיס.
    """
    print("\n[SETUP] Preparing API Environment...")
    
    # 1. יצירת סשן (מייעל ביצועים ושומר על נתוני התחברות)
    session = requests.Session()
    
    # 2. הגדרת כותרות קבועות (Headers) לכל הבקשות
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
        # "Authorization": f"Bearer {ConfigManager.get_token()}" # הכנה לטוקן בעתיד
    })
    
    # 3. משיכת הכתובת מתוך קובץ הקונפיגורציה
    # ודא שיש לך פונקציה מתאימה ב-ConfigManager, או שנה לפי המימוש שלך
    api_url = ConfigManager.get_env_data()["api_url"]
    
    # 4. הזרקת הסשן והכתובת לתוך מחלקת הטסט כדי שתוכל להשתמש ב- self.session
    if hasattr(request, "cls") and request.cls is not None:
        request.cls.session = session
        request.cls.api_url = api_url
        
    yield session # מחזירים את הסשן למקרה שרוצים להשתמש בו ישירות
    
    # 5. ניקוי: סגירת החיבורים בסיום הטסט
    print("\n[TEARDOWN] Closing API Session...")
    session.close()

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
                    item.cls._trace_saved = True  # מסמן ל-trace_manager לא לעצור שוב
                    print(f"[FAILURE] Trace saved: {filename}.zip")
                except Exception as e:
                    print(f"[WARNING] Failed to save trace: {e}")

        # 2. Mobile screenshot
        elif hasattr(item.cls, "driver") and item.cls.driver is not None:
            try:
                driver = item.cls.driver
                driver.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"{filename}_mobile.png"))
                print(f"\n[FAILURE] Mobile screenshot saved: {filename}_mobile.png")
            except Exception as e:
                print(f"\n[WARNING] Failed to capture mobile screenshot: {e}")

        # 3. API / DB → Failure Log (txt עם Traceback מלא)
        else:
            try:
                log_path = os.path.join(LOGS_DIR, f"{filename}_failure.txt")
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write(f"Test   : {item.nodeid}\n")
                    f.write(f"Time   : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n")
                    f.write(str(report.longrepr))
                print(f"[FAILURE] Failure log saved: {filename}_failure.txt")
            except Exception as e:
                print(f"[WARNING] Failed to save failure log: {e}")

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
