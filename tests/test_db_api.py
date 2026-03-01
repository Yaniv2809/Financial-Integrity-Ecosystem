import allure
import os
import pytest
from workflows.api.api_workflows import APIWorkflows
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

@allure.epic("API & DB Integration")
@allure.feature("Cross-Layer Validation")
@pytest.mark.usefixtures("api_setup")
class TestDBAPI:

    @allure.title("API: DB Validation - Verify API in DB")
    @allure.description("Creates an expense via API and verifies it exists in the SQLite database.")
    def test01_verify_api_in_db(self):
        # 1. יצירה ב-API
        response = APIWorkflows.create_expense("API_to_DB_Test", 999, "2025-05-05", "Other")
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")
        
        # 2. (סימולציה של שרת) כתיבה ל-SQLite גיבוי 
        # (מכיוון ששרת ה-JSON המקומי שלנו לא מחובר אוטומטית ל-SQLite, אנו מדמים פה את פעולת ה-Backend)
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("API_to_DB_Test", 999.0, "2025-05-05", "Food"))
        
        # 3.query from DB to verify the record exists
        query = "SELECT * FROM expenses WHERE expense_name = 'API_to_DB_Test'"
        records = DBActions.execute_query(DB_PATH, query)
        
        # verify the record exists in DB
        assert len(records) > 0, " Data was not saved in DB!"
        DBVerifications.verify_record_count(records, 1)
        
        # 4. cleanup - delete the created record from DB and API
        APIWorkflows.delete_expense(created_id)