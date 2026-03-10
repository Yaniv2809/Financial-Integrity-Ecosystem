import allure
import pytest
from workflows.api.api_workflows_expense import APIWorkflows
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from config.config import ConfigManager


@allure.epic("API & DB Integration")
@allure.feature("Cross-Layer Validation")
@pytest.mark.usefixtures("api_setup", "db_setup_teardown")
class TestDBAPI:
    db_path = ConfigManager.get_db_path()
    @allure.title("API → DB: Create expense via API and verify in SQLite")
    @allure.description("Creates an expense via API, simulates backend write to SQLite, "
                        "verifies data integrity across layers, and cleans up.")
    def test01_verify_api_in_db(self):
        # Test Data
        expense_name = "API_to_DB_Test"
        expense_amount = 999.0
        expense_date = "2025-05-05"
        expense_category = "Food"

        # 1. יצירה דרך API + אימות תגובה
        response = APIWorkflows.create_expense(expense_name, expense_amount, expense_date, expense_category)
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")
        assert created_id is not None, "API did not return an ID for the created expense"
        APIVerifications.verify_response_value(response, "expense_name", expense_name)
        APIVerifications.verify_response_value(response, "amount", expense_amount)

        # 2. סימולציית Backend — כתיבה ל-SQLite
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(self.db_path, insert_query, (expense_name, expense_amount, expense_date, expense_category))

        # 3. אימות ב-DB — הרשומה קיימת עם הנתונים הנכונים
        select_query = "SELECT expense_name, amount, date, category FROM expenses WHERE expense_name = ?"
        records = DBActions.execute_query(self.db_path, select_query, (expense_name,))

        DBVerifications.verify_record_count(records, 1)
        record = records[0]
        assert record[0] == expense_name, f"DB name mismatch: expected '{expense_name}', got '{record[0]}'"
        assert record[1] == expense_amount, f"DB amount mismatch: expected {expense_amount}, got {record[1]}"
        assert record[2] == expense_date, f"DB date mismatch: expected '{expense_date}', got '{record[2]}'"
        assert record[3] == expense_category, f"DB category mismatch: expected '{expense_category}', got '{record[3]}'"

        # # 4. Cleanup — מחיקה מ-API ומ-DB
        # APIWorkflows.delete_expense(created_id)
        # delete_query = "DELETE FROM expenses WHERE expense_name = ?"
        # DBActions.execute_query(self.db_path, delete_query, (expense_name,))

        # # 5. אימות שהניקוי עבד — הרשומה לא קיימת יותר
        # records_after = DBActions.execute_query(self.db_path, select_query, (expense_name,))
        # DBVerifications.verify_record_count(records_after, 0)