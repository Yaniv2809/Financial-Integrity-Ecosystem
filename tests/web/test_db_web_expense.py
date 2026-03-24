import pytest
import allure
from playwright.sync_api import expect
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from workflows.web.web_workflows_expense import WebWorkflows
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from config.config import ConfigManager


# conftest.py will handle the setup and teardown of the database connection and any necessary fixtures for the tests in this class, allowing us to focus on the test logic itself here in TestDBWeb without worrying about the underlying database operations or state management. This keeps our tests clean and focused on their specific purpose, while still ensuring that we have a known state in the database to work with for our Web UI tests.
@allure.epic("Web & DB Integration")
@allure.feature("Cross-Layer Validation")
@pytest.mark.db
@pytest.mark.web
@pytest.mark.integration
@pytest.mark.usefixtures("web_setup", "db_setup_teardown", "inject_web_course_record")
class TestDBWeb:
    db_path = ConfigManager.get_db_path()

    @allure.title("Web & DB: Inject full DB data to Web UI")
    @allure.description("Reads a complete record from SQLite and injects it into the expense tracker website.")
    def test01_web_driven_by_db(self):
        # 1. call DB
        query = "SELECT expense_name, amount, date, category FROM expenses WHERE expense_name = 'Web_Course'"
        records = DBActions.execute_query(self.db_path, query)
        DBVerifications.verify_record_count(records, expected_count=1)
        # 2. get data
        db_name, db_amount, db_date, db_category = records[0]
        db_amount_str = str(int(db_amount))
        print(f"\nPulled from DB: {db_name} | ${db_amount_str} | {db_date} | {db_category}")
        # 3. inject to Web UI
        WebWorkflows.create_expense(
            page=self.page, 
            expense_name=db_name, 
            amount=db_amount_str, 
            date=db_date, 
            category=db_category
        )
        
        # 4. full verify
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        expect(element["name"]).to_contain_text(db_name)
        expect(element["amount"]).to_contain_text(f"${db_amount_str}")
        expect(element["date"]).to_contain_text(db_date)
        expect(element["category"]).to_contain_text(db_category.lower())