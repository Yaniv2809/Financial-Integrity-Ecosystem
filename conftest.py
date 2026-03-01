from playwright.sync_api import Playwright
import pytest
from utils.logger import Logger
import os
from extensions.db_actions import DBActions
from config.config import ConfigManager

@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    # ------------------ SETUP ------------------
    log = Logger()
    log.info("====== SETUP: Starting Test Execution ======")
    yield  
    # ----------------- TEARDOWN -----------------
    log.info("====== TEARDOWN: Test Execution Completed ======")
    # AI can add any cleanup code here if needed in the future (e.g., closing database connections, clearing test data, etc.)

# הגדרת נתיבים גלובליים
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

# ==========================================
# 1. הגדרות מסד נתונים (DB) - רץ פעם אחת לכל הרצה
# ==========================================
@pytest.fixture(scope="session", autouse=True)
def db_setup_teardown():
    print("\n[SETUP] Initializing Global DB Environment...")
    # יצירת הטבלה אם אינה קיימת
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
    # ניקוי נתוני טסטים מה-DB כדי לשמור על סביבה נקייה להרצה הבאה
    DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name LIKE '%Test%'")


# ==========================================
# 2. הגדרות Web (Playwright) - רץ לפני כל טסט Web
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
    yield 
    print("\n[TEARDOWN] Closing Browser...")
    page.close()
    context.close()
    browser.close()

# ==========================================
# 3. הגדרות API - רץ לפני טסטים של API
# ==========================================
@pytest.fixture(scope="function")
def api_setup():
    """
    פיקסטור לטסטים של API.
    אפשר להוסיף כאן לוגיקה של התחברות לשרת, השגת טוקן (Token), או ניקוי.
    """
    print("\n[SETUP] Preparing API Environment...")
    # כרגע אין צורך בלוגיקה מורכבת כי ה-URL מוגדר ב-Workflows
    yield 
    print("\n[TEARDOWN] API Test Completed.")
