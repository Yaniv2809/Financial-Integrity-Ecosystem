import pytest
import os
import time
import json
import allure
import requests
from extensions.db_actions import DBActions
from config.config import ConfigManager
from workflows.api.api_workflows_expense import APIWorkflows
from utils.ai import get_ai_error_analysis 
from playwright.sync_api import Playwright
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# Global Paths
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = ConfigManager.get_db_path()
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "reports", "screenshots")
TRACES_DIR = os.path.join(PROJECT_ROOT, "reports", "traces")
LOGS_DIR = os.path.join(PROJECT_ROOT, "reports", "logs")

# יצירת תיקיות דוחות אם לא קיימות (חיוני למניעת קריסות בריצה ראשונה)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(TRACES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ==========================================
# CLI Options
# ==========================================
def pytest_addoption(parser):
    """מוסיף דגל מותאם אישית להרצת AI על שגיאות"""
    parser.addoption(
        "--ai-analysis", 
        action="store_true", 
        default=False, 
        help="Run AI analysis globally on all test failures"
    )

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
    is_ci = os.environ.get("CI") == "true"
    slow_mo_value = 1000
    if request.node.get_closest_marker("fast_browser"):
        slow_mo_value = 0
    headless = True if is_ci else False
    print(f"\n[SETUP] Launching Browser (headless={headless}, slow_mo={slow_mo_value})...")
    browser = playwright.chromium.launch(
        headless=headless,
        channel="chrome" if not is_ci else None,
        slow_mo=slow_mo_value
    )
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
class LoggingRetry(Retry):
    """
    מחלקה שעוטפת את מנגנון ה-Retry הרשמי ומדפיסה אזהרה לקונסול
    """
    # רמה 1: הזחה של 4 רווחים (פונקציה בתוך המחלקה)
    def increment(self, method=None, url=None, response=None, error=None, _pool=None, _stacktrace=None):
        # רמה 2: הזחה של 8 רווחים (הקוד של הפונקציה)
        retry_count = len(self.history) + 1
        print(f"\n[NETWORK HEALING] Triggering Retry {retry_count} for {method} {url}")
        
        if response:
            print(f"   -> Reason: Server returned Bad Status {response.status}")
        if error:
            print(f"   -> Reason: Network Error - {error}")
            
        return super().increment(method, url, response, error, _pool, _stacktrace)

# --- כאן הסתיימה המחלקה LoggingRetry ---

# רמה 0: ללא הזחה (הגדרת הפיקסטור)
@pytest.fixture(scope="function")
def api_setup(request):
    """
    פיקסטור לטסטים של API.
    מגדיר סשן עם מנגנון Retries חכם וגלוי.
    """
    # רמה 1: הזחה של 4 רווחים (הקוד של הפיקסטור)
    print("\n[SETUP] Preparing API Environment with Smart Retries...")
    
    session = requests.Session()
    
    # כאן אנחנו קוראים למחלקה שיצרנו למעלה!
    retries = LoggingRetry(
        total=3,                
        backoff_factor=1,       
        status_forcelist=[500, 502, 503, 504], 
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"] 
    )
    
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    api_url = ConfigManager.get_env_data()["api_url"]
    
    if hasattr(request, "cls") and request.cls is not None:
        request.cls.session = session
        request.cls.api_url = api_url
        
    yield session 
    
    print("\n[TEARDOWN] Closing API Session...")
    session.close()

@pytest.fixture(scope="function")
def api_cleanup():
    yield
    print("\n[TEARDOWN] Cleaning up API Test Data...")

@pytest.fixture(scope="function")
def api_token():
    return "Bearer dummy_token_for_testing"

@pytest.fixture(scope="function")
def temp_expense_id(api_setup):
    session = api_setup  # מקבלים את הסשן מהפיקסטור הראשי

    response = APIWorkflows.create_expense(session, "Temp_Expense", 999, "2025-12-31", "Testing")
    expense_id = response.json().get("id")
    
    yield expense_id

    APIWorkflows.delete_expense(session, expense_id)


@pytest.fixture(scope="function")
def smart_expense_id(api_setup):
    """
    פיקסטור חכם שמשתמש בהוצאה קיימת ממחלקת הטסטים אם ישנה,
    או יוצר אחת זמנית אם הטסט רץ בנפרד.
    """
    from tests.api.test_api_expense import TestAPI
    
    session = api_setup  # מקבלים את הסשן מהפיקסטור הראשי

    if TestAPI.created_id is not None:
        # ריצת מחלקה - test02 כבר יצר את ההוצאה
        yield TestAPI.created_id
        # אין cleanup - test06 ידאג למחיקה
    else:
        # ריצה עצמאית - יוצר הוצאה זמנית עם cleanup אוטומטי
        response = APIWorkflows.create_expense(session, "Temp_Expense", 999, "2025-12-31", "Testing")
        temp_id = response.json().get("id")
        
        yield temp_id
        
        APIWorkflows.delete_expense(session, temp_id)  # cleanup רק בריצה עצמאית

# ==========================================
# 4. Mobile Fixtures (Appium) - Class scope
# ==========================================
@pytest.fixture(scope="class")
def mobile_driver(request):
    from appium import webdriver as appium_webdriver
    from appium.options.android import UiAutomator2Options
    from data.mobile.mobile import MOBILE_CAPS, APPIUM_SERVER, TIMEOUT

    # תוקן: קריאה למשתנה שלא נשמר
    # sdk_path = ConfigManager.get_env_data().get('android_sdk_path')
    
    print("\n[SETUP] Launching Official Appium Server Driver...")
    options = UiAutomator2Options().load_capabilities(MOBILE_CAPS)
    
    driver = appium_webdriver.Remote(APPIUM_SERVER, options=options)
    driver.implicitly_wait(TIMEOUT)
    request.cls.driver = driver

    yield driver

    print("\n[TEARDOWN] Closing Appium Driver...")
    driver.quit()

# ==========================================
# 5. Screenshot, Trace & AI on Failure
# ==========================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        test_name = item.name
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}"

        # 1. Web screenshot + trace
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
                    item.cls._trace_saved = True  
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

        # 3. API / DB → Failure Log 
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
        # 4. AI ERROR ANALYSIS 🤖
        # ==========================================
        is_global_ai_enabled = item.config.getoption("--ai-analysis")
        has_ai_marker = item.get_closest_marker("use_ai") is not None
        
        if is_global_ai_enabled or has_ai_marker:
            # תוקן: שימוש ב-longrepr כדי לתת למודל את כל הקונטקסט של השגיאה, לא רק את השורה האחרונה
            full_traceback = str(report.longrepr)
            print(f"\n[AI Analysis] Triggering Groq for failure in {test_name}... please wait...")            
            
            try:
                ai_explanation = get_ai_error_analysis(full_traceback)
                
                print("\n============= AI ERROR ANALYSIS =============")
                print(ai_explanation)
                print("=============================================\n")
                
                # סיווג באג מובנה
                test_layer = "unknown"
                if hasattr(item.cls, "page"):
                    test_layer = "Web/UI"
                elif hasattr(item.cls, "driver"):
                    test_layer = "Mobile"
                elif "api" in item.nodeid.lower():
                    test_layer = "API"
                elif "db" in item.nodeid.lower():
                    test_layer = "Database"

                from utils.ai_test_generator import AITestGenerator
                classification = AITestGenerator.classify_bug(full_traceback, test_layer)

                if isinstance(classification, dict) and "bug_type" in classification:
                    print(f"\n[BUG CLASSIFICATION]")
                    print(f"  Type:     {classification['bug_type']}")
                    print(f"  Severity: {classification['severity']}")
                    print(f"  Category: {classification['category']}")
                    print(f"  Summary:  {classification['summary']}")
                    print(f"  Fix:      {classification['suggested_fix']}")

                classification_str = json.dumps(classification, indent=2, ensure_ascii=False) if isinstance(classification, dict) else str(classification)

                allure.attach(
                    body=f"=== Raw Error ===\n{full_traceback}\n\n=== 🤖 AI Analysis ===\n{ai_explanation}\n\n=== Bug Classification ===\n{classification_str}",
                    name="🤖 AI Failure Analysis & Classification",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                print(f"[WARNING] AI Analysis failed to execute: {e}")