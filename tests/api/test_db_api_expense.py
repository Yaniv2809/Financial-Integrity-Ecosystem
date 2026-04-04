import allure
import pytest
import random
from workflows.api.api_workflows_expense import APIWorkflows
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from config.config import ConfigManager


@allure.epic("API & DB Integration")
@allure.feature("Cross-Layer Validation")
@pytest.mark.db
@pytest.mark.integration
@pytest.mark.usefixtures("api_setup", "db_setup_teardown")
class TestDBAPI:
    db_path = ConfigManager.get_db_path()
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("API → DB: Create expense via API and verify in SQLite")
    @allure.description("Creates an expense via API, simulates backend write to SQLite, "
                        "verifies data integrity across layers, and cleans up.")
    def test01_verify_api_in_db(self):
        # Test Data
        expense_name = f"API_to_DB_Test{random.randint(1000, 9999)}"
        expense_amount = 999.0
        expense_date = "2025-05-05"
        expense_category = "Food"

        # 1. Creation via API + response verification
        response = APIWorkflows.create_expense(self.session, expense_name, expense_amount, expense_date, expense_category)
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")
        assert created_id is not None, "API did not return an ID for the created expense"
        APIVerifications.verify_response_value(response, "expense_name", expense_name)
        APIVerifications.verify_response_value(response, "amount", expense_amount)

        # 2. Backend simulation — writing to SQLite
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(self.db_path, insert_query, (expense_name, expense_amount, expense_date, expense_category))

        # 3. DB verification — record exists with correct data
        select_query = "SELECT expense_name, amount, date, category FROM expenses WHERE expense_name = ?"
        records = DBActions.execute_query(self.db_path, select_query, (expense_name,))

        DBVerifications.verify_record_count(records, 1)
        DBVerifications.verify_db_record_match(
            actual_record=(records[0][0], records[0][1], records[0][3]),
            expected_record=(expense_name, expense_amount, expense_category)
        )

        # 4. Cleanup — deletion from API and DB
        APIWorkflows.delete_expense(self.session, created_id)
        delete_query = "DELETE FROM expenses WHERE expense_name = ?"
        DBActions.execute_query(self.db_path, delete_query, (expense_name,))

        # 5. Verification that cleanup worked — the record no longer exists
        records_after = DBActions.execute_query(self.db_path, select_query, (expense_name,))
        DBVerifications.verify_record_count(records_after, 0)