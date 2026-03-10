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
    """מחזיר את ה-URL של Flask server (port 5000) שכותב לאותו SQLite."""
    return ConfigManager.get_env_data()["flask_api_url"]


@allure.epic("E2E Integration")
@allure.feature("API ↔ DB Data Integrity")
@pytest.mark.e2e
@pytest.mark.usefixtures("api_setup")
class TestE2EApiDb:
    """
    טסטי אינטגרציה אמיתיים בין Flask API ל-SQLite.
    Flask server (port 5000) כותב וקורא ישירות מ-expense_db.db —
    לא json-server (port 3000) שמשתמש ב-db.json נפרד.
    כל טסט עצמאי עם cleanup מובנה.
    """
    db_path = ConfigManager.get_db_path()

    # ============================================================
    # E2E_01: POST דרך API → רשומה מופיעה ב-DB
    # ============================================================
    @allure.title("E2E_01: API → DB | POST creates record in SQLite")
    @allure.description(
        "יוצר הוצאה דרך ה-API ומוודא שהרשומה הופיעה ב-SQLite ללא כתיבה ישירה לDB. "
        "מאמת שה-API אכן כותב לשכבת הנתונים."
    )
    def test01_api_create_reflects_in_db(self):
        expense_name = f"E2E_API_to_DB_{random.randint(1000, 9999)}"
        expense_amount = round(random.uniform(10, 500), 2)
        expense_date = "2026-01-15"
        expense_category = "Education"
        created_id = None

        try:
            # שלב 1: יצירה דרך Flask API בלבד
            response = requests.post(_flask_url(), json={
                "expense_name": expense_name, "amount": expense_amount,
                "date": expense_date, "category": expense_category
            })
            APIVerifications.verify_status_code(response, 201)
            created_id = response.json().get("id")
            assert created_id is not None, "API did not return an ID for the created expense"

            # שלב 2: שליפה ישירה מה-DB לפי ID שחזר מה-API
            records = DBActions.execute_query(
                self.db_path,
                "SELECT expense_name, amount, category FROM expenses WHERE id = ?",
                (created_id,)
            )

            # שלב 3: אימות שהרשומה קיימת ב-DB עם הנתונים הנכונים
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
    # E2E_02: INSERT ישיר ל-DB → רשומה נגישה דרך ה-API
    # ============================================================
    @allure.title("E2E_02: DB → API | INSERT in SQLite is readable via GET")
    @allure.description(
        "מזריק רשומה ישירות ל-SQLite ומוודא שה-API מחזיר אותה. "
        "מאמת שה-API קורא את הנתונים מ-DB בצורה נכונה."
    )
    def test02_db_insert_reflects_in_api(self):
        expense_name = f"E2E_DB_to_API_{random.randint(1000, 9999)}"
        expense_amount = 250.0
        expense_date = "2026-02-20"
        expense_category = "Transportation"

        try:
            # שלב 1: הזרקה ישירה ל-DB ללא שימוש ב-API
            DBActions.execute_query(
                self.db_path,
                "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)",
                (expense_name, expense_amount, expense_date, expense_category)
            )

            # שלב 2: שליפת כל ההוצאות דרך Flask API
            response = requests.get(_flask_url())
            APIVerifications.verify_status_code(response, 200)

            # שלב 3: אימות שהרשומה שהוזרקה נמצאת בתגובת ה-API
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
    # E2E_03: PUT דרך API → שינוי נשמר ב-DB
    # ============================================================
    @allure.title("E2E_03: API → DB | PUT updates record in SQLite")
    @allure.description(
        "מעדכן הוצאה קיימת דרך ה-API ומוודא שהשינוי נשמר ב-SQLite. "
        "מאמת שעדכון API מסתנכרן לשכבת הנתונים."
    )
    def test03_api_update_reflects_in_db(self):
        original_name = f"E2E_Pre_Update_{random.randint(1000, 9999)}"
        updated_name = f"E2E_Post_Update_{random.randint(1000, 9999)}"
        created_id = None

        try:
            # שלב 1: יצירת הרשומה המקורית דרך Flask
            response = requests.post(_flask_url(), json={
                "expense_name": original_name, "amount": 100.0,
                "date": "2026-01-01", "category": "Food"
            })
            APIVerifications.verify_status_code(response, 201)
            created_id = response.json().get("id")

            # שלב 2: עדכון דרך Flask API
            update_response = requests.put(f"{_flask_url()}/{created_id}", json={
                "expense_name": updated_name, "amount": 200.0,
                "date": "2026-03-01", "category": "Fashion"
            })
            APIVerifications.verify_status_code(update_response, 200)

            # שלב 3: שליפה ישירה מ-DB ואימות שהעדכון נשמר
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
    # E2E_04: DELETE דרך API → רשומה נמחקת מה-DB
    # ============================================================
    @allure.title("E2E_04: API → DB | DELETE removes record from SQLite")
    @allure.description(
        "מוחק הוצאה דרך ה-API ומוודא שהרשומה נמחקה מ-SQLite. "
        "מאמת שמחיקת API מסתנכרנת לשכבת הנתונים."
    )
    def test04_api_delete_reflects_in_db(self):
        expense_name = f"E2E_Delete_Test_{random.randint(1000, 9999)}"

        # שלב 1: יצירה דרך Flask
        response = requests.post(_flask_url(), json={
            "expense_name": expense_name, "amount": 75.0,
            "date": "2026-01-10", "category": "Accommodation"
        })
        APIVerifications.verify_status_code(response, 201)
        created_id = response.json().get("id")

        # שלב 2: מחיקה דרך Flask API
        delete_response = requests.delete(f"{_flask_url()}/{created_id}")
        APIVerifications.verify_status_code(delete_response, 200)

        # שלב 3: אימות ישיר ב-DB שהרשומה לא קיימת יותר
        records = DBActions.execute_query(
            self.db_path,
            "SELECT id FROM expenses WHERE id = ?",
            (created_id,)
        )
        DBVerifications.verify_record_count(records, 0)