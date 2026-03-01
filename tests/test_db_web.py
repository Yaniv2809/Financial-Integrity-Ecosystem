import pytest
import allure
import os
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from workflows.web.web_workflows import WebWorkflows
from extensions.web_verification import WebVerify

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

# conftest.py will handle the setup and teardown of the database connection and any necessary fixtures for the tests in this class, allowing us to focus on the test logic itself here in TestDBWeb without worrying about the underlying database operations or state management. This keeps our tests clean and focused on their specific purpose, while still ensuring that we have a known state in the database to work with for our Web UI tests.
@pytest.mark.usefixtures("web_setup")
class TestDBWeb:
    # only for this test class, we will inject specific data into the DB before the test and clean it up after, simulating a backend operation that would normally happen when creating an expense through the API or Web UI - this allows us to have a known record in the DB to work with for our Web UI test, without relying on the API to create it for us (which is what we are actually trying to test here - that the Web UI can correctly display data from the DB)
    @pytest.fixture(scope="function", autouse=True)
    def inject_test_data(self):
        print("\n[SETUP] Injecting specific record for TestDBWeb...")
        
        # 1. delete any existing record with the same name to ensure a clean state for the test (simulating a backend cleanup operation that would normally happen before creating a new expense through the API or Web UI)
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")
        
        # 2. insert a specific record to be used in the test (simulating a backend operation that would normally happen when creating an expense through the API or Web UI) - this is our "source of truth" for the test
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("Web_Course", 1500.0, "2026-02-25", "Education"))
        yield  
        print("\n[TEARDOWN] Cleaning up specific record after TestDBWeb...")
        # 3. cleanup
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")


    @allure.title("Web & DB: Inject full DB data to Web UI")
    @allure.description("Reads a complete record from SQLite and injects it into the expense tracker website.")
    def test01_web_driven_by_db(self):
        # 1. query the DB to get the specific record we injected in the setup 
        query = "SELECT * FROM expenses WHERE expense_name = 'Web_Course'"
        records = DBActions.execute_query(DB_PATH, query)
        DBVerifications.verify_record_count(records, expected_count=1)
        
        # 2. taking the values from the DB record to use in the Web UI
        db_name = records[0][1]
        db_amount = str(int(records[0][2])) 
        db_date = records[0][3]
        db_category = records[0][4]
        
        print(f"\n Pulled from DB: {db_name} | ${db_amount} | {db_date} | {db_category}")
        
        # 3. injecting the DB data into the Web UI using the existing workflow for creating an expense
        WebWorkflows.create_expense(
            page=self.page, 
            description=db_name, 
            amount=db_amount, 
            date=db_date, 
            category=db_category
        )
        
        # 4. verify the injected data appears correctly in the Web UI
        element_to_verify = self.page.locator(f"text={db_name}")
        WebVerify.text(element_to_verify, db_name)