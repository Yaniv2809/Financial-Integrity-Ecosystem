import pytest
import allure
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from config.config import ConfigManager
from workflows.web.web_workflows import WebWorkflows
from extensions.web_verification import WebVerify
import os

#this command is used to get the project root directory regardless of where the test is run from, ensuring the DB path is always correct
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

class TestDBWeb:
    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        print("\n[SETUP] Preparing DB for Web Test...")
        # 1. create the table if it doesn't exist, clear any old test data, and insert the specific record this test needs
        DBActions.execute_query(DB_PATH, "CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, expense_name TEXT, amount REAL, date TEXT, category TEXT)")
        
        # 2. clean up any old test data to avoid duplicates and ensure a consistent test environment
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")
        
        # 3. insert the specific record that this test will read and use to create an expense in the web UI
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("Web_Course", 1500.0, "2026-02-25", "Education"))
        yield  
        print("\n[TEARDOWN] Cleaning up Web Test data...")
        # 4. clean up the test data after the test runs to keep the DB clean for future tests
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")



    @allure.title("Web & DB: Inject DB data to Web UI")
    @allure.description("Reads 'Web_Course' from SQLite and injects it into the expense tracker website.")
    def test01_web_driven_by_db(self, page):

        query = "SELECT * FROM expenses WHERE expense_name = 'Web_Course'"
        records = DBActions.execute_query(DB_PATH, query)
        DBVerifications.verify_record_count(records, expected_count=1)
        db_name = records[0][1]
        db_amount = str(int(records[0][2]))
        print(f"\n Pulled from DB: {db_name} - ${db_amount}")
        page.goto(ConfigManager.get_env_data()['web_url'])
        
        WebWorkflows.create_expense(
            page=page, 
            description=db_name, 
            amount=db_amount, 
            date="2025-10-10", 
            category="Education"
        )
        page.click(ExpenseTrackerPage.btn_add)
        page.wait_for_timeout(500) #wait a bit for the UI to update
        element_to_verify = page.locator(f"text={db_name}")
        WebVerify.text(element_to_verify, db_name)