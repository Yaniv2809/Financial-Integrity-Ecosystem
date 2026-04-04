import allure
import pytest
import random
import requests
from smart_assertions import soft_assert, verify_expectations
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from config.config import ConfigManager


def _flask_url():
    """Returns the URL of the Flask server (port 5000) that writes to the same SQLite."""
    return ConfigManager.get_env_data()["flask_api_url"]


@allure.epic("E2E Integration")
@allure.feature("API ↔ DB Data Integrity")
@pytest.mark.e2e
@pytest.mark.usefixtures("api_setup")
class TestE2EApiDb:
    """
    Real integration tests between Flask API and SQLite.
    Flask server (port 5000) writes and reads directly from expense_db.db —
    not json-server (port 3000) which uses a separate db.json.
    Each test is independent with built-in cleanup.

    """
    db_path = ConfigManager.get_db_path()

    # ============================================================
    # E2E_01: POST דרך API → רשומה מופיעה ב-DB
    # ============================================================
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("E2E_01: API → DB | POST creates record in SQLite")
    @allure.description(
        "Creates an output via the API and verifies that the record appeared in SQLite without writing directly to the DB. "
"Verifies that the API is actually writing to the data layer."
    )
    def test01_api_create_reflects_in_db(self):
        expense_name = f"E2E_API_to_DB_{random.randint(1000, 9999)}"
        expense_amount = round(random.uniform(10, 500), 2)
        expense_date = "2026-01-15"
        expense_category = "Education"
        created_id = None

        try:
            # Step 1: Create via Flask API only
            response = requests.post(_flask_url(), json={
                "expense_name": expense_name, "amount": expense_amount,
                "date": expense_date, "category": expense_category
            })
            APIVerifications.verify_status_code(response, 201)
            created_id = response.json().get("id")
            assert created_id is not None, "API did not return an ID for the created expense"

            # Step 2: Direct retrieval from the DB by ID returned from the API
            records = DBActions.execute_query(
                self.db_path,
                "SELECT expense_name, amount, category FROM expenses WHERE id = ?",
                (created_id,)
            )

            # Step 3: Verify that the record exists in the DB with the correct data
            DBVerifications.verify_record_count(records, 1)
            DBVerifications.verify_db_record_match(
                actual_record=(records[0][0], records[0][1], records[0][2]),
                expected_record=(expense_name, expense_amount, expense_category)
            )
            verify_expectations()

        finally:
            if created_id:
                requests.delete(f"{_flask_url()}/{created_id}")

    # ============================================================
    # E2E_02: Direct INSERT to DB → Record accessible via API
    # ============================================================
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("E2E_02: DB → API | INSERT in SQLite is readable via GET")
    @allure.description(
        "Injects a record directly into SQLite and verifies that the API returns it. "
"Verifies that the API reads the data from the DB correctly."
    )
    def test02_db_insert_reflects_in_api(self):
        expense_name = f"E2E_DB_to_API_{random.randint(1000, 9999)}"
        expense_amount = 250.0
        expense_date = "2026-02-20"
        expense_category = "Transportation"

        try:
            # Step 1: Direct injection into the DB without using the API
            DBActions.execute_query(
                self.db_path,
                "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)",
                (expense_name, expense_amount, expense_date, expense_category)
            )

            # Step 2: Retrieving all expenses via Flask API
            response = requests.get(_flask_url())
            APIVerifications.verify_status_code(response, 200)

            # Step 3: Verify that the inserted record is returned by the API
            expenses = response.json()
            matching = [e for e in expenses if e.get("expense_name") == expense_name]

            soft_assert(len(matching) == 1, f"Expected 1 record in API for '{expense_name}', found {len(matching)}")
            if matching:
                soft_assert(matching[0]["amount"] == expense_amount, f"Amount mismatch: expected {expense_amount}, got {matching[0]['amount']}")
                soft_assert(matching[0]["category"] == expense_category, f"Category mismatch: expected '{expense_category}', got {matching[0]['category']}")
            verify_expectations()

        finally:
            DBActions.execute_query(
                self.db_path,
                "DELETE FROM expenses WHERE expense_name = ?",
                (expense_name,)
            )

    # ============================================================
    # E2E_03: PUT via API → Change saved in DB
    # ============================================================
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("E2E_03: API → DB | PUT updates record in SQLite")
    @allure.description(
        "Updates an existing expense via the API and verifies that the change is saved in SQLite. "
        "Verifies that the API update is synchronized with the data layer."
    )
    def test03_api_update_reflects_in_db(self):
        original_name = f"E2E_Pre_Update_{random.randint(1000, 9999)}"
        updated_name = f"E2E_Post_Update_{random.randint(1000, 9999)}"
        created_id = None

        try:
            # Step 1: Create the original record via Flask
            response = requests.post(_flask_url(), json={
                "expense_name": original_name, "amount": 100.0,
                "date": "2026-01-01", "category": "Food"
            })
            APIVerifications.verify_status_code(response, 201)
            created_id = response.json().get("id")

            # Step 2: Update via Flask API
            update_response = requests.put(f"{_flask_url()}/{created_id}", json={
                "expense_name": updated_name, "amount": 200.0,
                "date": "2026-03-01", "category": "Fashion"
            })
            APIVerifications.verify_status_code(update_response, 200)

            # Step 3: Direct retrieval from the DB and verify the update
            records = DBActions.execute_query(
                self.db_path,
                "SELECT expense_name, amount, category FROM expenses WHERE id = ?",
                (created_id,)
            )
            DBVerifications.verify_record_count(records, 1)
            DBVerifications.verify_db_record_match(
                actual_record=(records[0][0], records[0][1], records[0][2]),
                expected_record=(updated_name, 200.0, "Fashion")
            )
            verify_expectations()

        finally:
            if created_id:
                requests.delete(f"{_flask_url()}/{created_id}")

    # ============================================================
    # E2E_04: DELETE via API → Record is deleted from the DB
    # ============================================================
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("E2E_04: API → DB | DELETE removes record from SQLite")
    @allure.description(
        "Deletes an expense via the API and verifies that the record is removed from SQLite. "
        "Verifies that the API delete is synchronized with the data layer."
    )
    def test04_api_delete_reflects_in_db(self):
        expense_name = f"E2E_Delete_Test_{random.randint(1000, 9999)}"

        # Step 1: Create via Flask
        response = requests.post(_flask_url(), json={
            "expense_name": expense_name, "amount": 75.0,
            "date": "2026-01-10", "category": "Accommodation"
        })
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")

        # Step 2: Delete via Flask API
        delete_response = requests.delete(f"{_flask_url()}/{created_id}")
        APIVerifications.verify_status_code(delete_response, 200)

        # Step 3: Direct verification in the DB that the record no longer exists
        records = DBActions.execute_query(
            self.db_path,
            "SELECT id FROM expenses WHERE id = ?",
            (created_id,)
        )
        DBVerifications.verify_record_count(records, 0)

    # ============================================================
    # E2E_05: Data Integrity — Set Theory & ACID
    # ============================================================
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("E2E_05: API & DB Data Integrity: Set Theory & ACID")
    @allure.description(
        "Verifies that the total expenses are updated correctly, "
        "and that the new record can be isolated using set theory (Set Difference)."
    )
    def test05_data_integrity_with_set_theory(self):
        expense_name = "Integrity_Check_Expense"
        expense_amount = 100

        # ==========================================
        # PRE-CONDITION: Saving the current state in the DB
        # ==========================================

        # A. Total existing expenses (for ACID consistency check)
        sum_query = "SELECT SUM(amount) FROM expenses"
        initial_sum_result = DBActions.execute_query(self.db_path, sum_query)
        initial_total = initial_sum_result[0][0] if (initial_sum_result and initial_sum_result[0][0] is not None) else 0.0

        # B. Set of all existing expense names (Set A)
        all_names_query = "SELECT expense_name FROM expenses"
        initial_records = DBActions.execute_query(self.db_path, all_names_query)
        initial_set = set([str(row[0]) for row in initial_records])

        # ==========================================
        # ACTION: Create an expense via Flask API
        # ==========================================
        response = requests.post(_flask_url(), json={
            "expense_name": expense_name, "amount": expense_amount,
            "date": "2026-05-05", "category": "Food"
        })
        APIVerifications.verify_status_code(response, 201)

        # ==========================================
        # POST-CONDITION: The new state in the DB (Set B)
        # ==========================================
        final_sum_result = DBActions.execute_query(self.db_path, sum_query)
        final_total = final_sum_result[0][0]

        final_records = DBActions.execute_query(self.db_path, all_names_query)
        final_set = set([str(row[0]) for row in final_records])

        # ==========================================
        # VALIDATIONS: Data integrity set theory
        # ==========================================
        try:
            # 1. Mathematical validation (ACID - Consistency)
            expected_total = initial_total + expense_amount
            assert final_total == expected_total, \
                f"DB Math Error! Expected {expected_total}, Got {final_total}"

            # 2. Set Difference: B - A = Exactly one record
            newly_added_records = final_set - initial_set
            assert len(newly_added_records) == 1, \
                f"Set Error! Expected 1 new record, got {len(newly_added_records)}"

            # 3. The added record is indeed the one we created.
            isolated_record = newly_added_records.pop()
            assert isolated_record == expense_name, \
                f"Mismatch! Expected '{expense_name}', Got '{isolated_record}'"

        finally:
            DBActions.execute_query(
                self.db_path,
                "DELETE FROM expenses WHERE expense_name = ?",
                (expense_name,)
            )




