import allure
import os
import pytest
from workflows.api.api_workflows_expense import APIWorkflows
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

@allure.epic("API & DB Integration")
@allure.feature("Cross-Layer Validation")

class TestDBAPI:

    @allure.title("API→DB: CREATE - Verify expense written to DB by server")
    @allure.description(
        "Creates an expense via API and verifies the Flask server actually persisted it "
        "in SQLite — no manual DB insert. True data integrity check."
    )
    def test01_create_via_api_verify_in_db(self):
        # 1. Create via API (Flask server writes to SQLite)
        response = APIWorkflows.create_expense("API_to_DB_Test", 999, "2025-05-05", "Other")
        APIVerifications.verify_status_code(response, 200)
        created_id = response.json().get("id")
        assert created_id is not None, "API did not return an ID for the created expense"

        # 2. Query DB directly — no manual insert, server must have done it
        records = DBActions.execute_query(
            DB_PATH,
            "SELECT * FROM expenses WHERE id = ?",
            (created_id,)
        )

        # 3. Verify the record exists in DB with correct values
        DBVerifications.verify_record_count(records, 1)
        row = records[0]
        assert row[1] == "API_to_DB_Test", f"expense_name mismatch: {row[1]}"
        assert row[2] == 999.0,            f"amount mismatch: {row[2]}"
        assert row[3] == "2025-05-05",     f"date mismatch: {row[3]}"
        assert row[4] == "Other",          f"category mismatch: {row[4]}"

        # 4. Cleanup
        APIWorkflows.delete_expense(created_id)

    @allure.title("API→DB: DELETE - Verify expense removed from DB by server")
    @allure.description(
        "Creates an expense via API, deletes it via API, and verifies the Flask server "
        "removed it from SQLite. True data integrity check."
    )
    def test02_delete_via_api_verify_removed_from_db(self):
        # 1. Create an expense to delete
        response = APIWorkflows.create_expense("Delete_Test", 50, "2025-06-01", "Food")
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")

        # 2. Delete via API
        delete_response = APIWorkflows.delete_expense(created_id)
        APIVerifications.verify_status_code(delete_response, 200)

        # 3. Verify it is gone from DB
        records = DBActions.execute_query(
            DB_PATH,
            "SELECT * FROM expenses WHERE id = ?",
            (created_id,)
        )
        assert len(records) == 0, f"Expense id={created_id} still exists in DB after DELETE via API!"

    @allure.title("API→DB: UPDATE - Verify updated values persisted in DB by server")
    @allure.description(
        "Creates an expense via API, updates it via API, and verifies the Flask server "
        "persisted the new values in SQLite. True data integrity check."
    )
    def test03_update_via_api_verify_in_db(self):
        # 1. Create
        response = APIWorkflows.create_expense("Update_Test_Original", 100, "2025-07-01", "Food")
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")

        # 2. Update via API
        update_response = APIWorkflows.update_expense(
            created_id, "Update_Test_Modified", 250, "2025-08-15", "Travel"
        )
        APIVerifications.verify_status_code(update_response, 200)

        # 3. Verify new values in DB
        records = DBActions.execute_query(
            DB_PATH,
            "SELECT * FROM expenses WHERE id = ?",
            (created_id,)
        )
        DBVerifications.verify_record_count(records, 1)
        row = records[0]
        assert row[1] == "Update_Test_Modified", f"expense_name not updated in DB: {row[1]}"
        assert row[2] == 250.0,                  f"amount not updated in DB: {row[2]}"
        assert row[3] == "2025-08-15",           f"date not updated in DB: {row[3]}"
        assert row[4] == "Travel",               f"category not updated in DB: {row[4]}"

        # 4. Cleanup
        APIWorkflows.delete_expense(created_id)




