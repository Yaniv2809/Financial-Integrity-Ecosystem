from playwright.async_api import Playwright
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
    
    yield # כאן רצים כל הטסטים ⏸️
    
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
    
    yield # ⏸️
    
    print("\n[TEARDOWN] API Test Completed.")
# import json
# import os
# import pytest
# from pytest import FixtureRequest
# from playwright.sync_api import Playwright
# from config.config import ConfigManager
# from workflows.api.api_workflows import APIWorkflows
# from workflows.web.web_workflows import WebWorkflows

# def load_config():
#     """Loads the configuration from config.json and returns it as a dictionary."""
#     # Get the absolute path of the current directory where conftest.py is located
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#     # Construct the correct path for config.json (move up one level if necessary)
#     CONFIG_PATH = os.path.join(BASE_DIR, "../config/config.json")

#     print(f"DEBUG: Looking for config.json at {CONFIG_PATH}")

#     # Load the configuration from config.json
#     try:
#         with open(CONFIG_PATH, "r") as config_file:
#             return json.load(config_file)
#     except FileNotFoundError as e:
#         raise FileNotFoundError(f"ERROR: Could not find config.json {CONFIG_PATH}") from e
    
# # Load the configuration
# CONFIG = load_config()     

# @pytest.fixture(autouse=True, scope="class")
# def setup(self, playwright: Playwright):
#         global browser, context, page
#         browser = playwright.chromium.launch(headless=False, channel="chrome", slow_mo=1000)
#         context = browser.new_context()
#         page = context.new_page()
#         url = ConfigManager.get_env_data()['web_url']
#         page.goto(url)
#         yield
#         context.close()
#         page.close()

# @pytest.fixture(scope= "class")
# def request_context(playwright: Playwright, request:FixtureRequest):
#     request_context=playwright.request.new_context(base_url=CHUCK_BASE_URL)
#     yield request_context
#     request_context.dispose()


# @pytest.fixture
# def expense_flows(page):
#     return WebWorkflows(page)


# @pytest.fixture
# def api_flows(request_context):
#     return APIWorkflows(request_context)
