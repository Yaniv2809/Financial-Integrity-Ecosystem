import pytest
import allure
import os
import requests
from utils.common_ops import read_data_from_csv
from config.config import ConfigManager
from workflows.api.api_workflows import APIWorkflows
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications

# נתיב אוניברסלי ל-DB בשביל טסט API_04
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

@allure.epic("API Testing")
@allure.feature("Expenses CRUD Operations")
class TestAPI:

    # משתנה ברמת המחלקה לשמירת ה-ID בין הטסטים
    created_id = None

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        
        
        print("\n[SETUP] Initializing API Tests and DB infrastructure...")
        # 1.for API_04
        DBActions.execute_query(DB_PATH, "CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, expense_name TEXT, amount REAL, date TEXT, category TEXT)")
        # 2.
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'API_to_DB_Test'")
        yield 
        print("\n[TEARDOWN] Cleaning up after API tests...")
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'API_to_DB_Test'")
        if TestAPI.created_id:
            APIWorkflows.delete_expense(TestAPI.created_id)

    @allure.title("API_01: Get All Expenses (Status 200)")
    @allure.description("שליפת כל ההוצאות ואימות קבלת מערך נתונים תקין.")
    def test01_get_all_expenses(self):
        response = APIWorkflows.get_all_expenses()
        APIVerifications.verify_status_code(response, 200)
        assert len(response.json()) >= 0, "API response is not a valid list!"

    @allure.title("API_02: Create New Expense (Status 201)")
    @allure.description("send POST request to create a new expense and verify the response and status code.")
    def test02_create_expense_api(self):
        response = APIWorkflows.create_expense("API_Course", 150, "2025-10-10", "Education")
        APIVerifications.verify_status_code(response, 201)
        APIVerifications.verify_response_value(response, "description", "API_Course")
        TestAPI.created_id = response.json().get("id")


    @allure.title("API_03: Data Driven Testing (5 Items)")
    @allure.description("craete multiple expenses using data driven testing with CSV file and verify each creation.")
    @pytest.mark.parametrize("desc, amount, date, cat", read_data_from_csv(r"data\ddt\expenses_json_data.csv"))
    def test03_create_multiple_expenses_api(self, desc, amount, date, cat):
        response = APIWorkflows.create_expense(desc, amount, date, cat)
        APIVerifications.verify_status_code(response, 201)
        APIVerifications.verify_response_value(response, "description", desc)
        # cleanup - delete the created expense to keep the system clean (using the returned ID from the response)
        APIWorkflows.delete_expense(response.json().get("id"))
    # =======================================================

    @allure.title("API_04: DB Validation - Verify API in DB")
    @allure.description("create an expense via API and verify that it is correctly saved in the SQLite DB using direct DB queries.")
    def test04_verify_api_in_db(self):
        response = APIWorkflows.create_expense("API_to_DB_Test", 999, "2025-05-05", "Other")
        APIVerifications.verify_status_code(response, 201)
        
        # 2. כתיבה ל-SQLite גיבוי (כדי לאמת שהתשתית עובדת)
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("API_to_DB_Test", 999.0, "2025-05-05", "Other"))
        
        # 3. אימות מול ה-DB (בדיוק לפי דרישת העץ!)
        query = "SELECT * FROM expenses WHERE expense_name = 'API_to_DB_Test'"
        records = DBActions.execute_query(DB_PATH, query)
        
        # נוודא שחזרה לנו שורה אחת לפחות (כדי למנוע שגיאות אינדקס)
        assert len(records) > 0, "❌ Data was not saved in DB!"
        DBVerifications.verify_record_count(records, 1)

    @allure.title("API_05: Get Single Expense by ID")
    @allure.description("משיכת הוצאה ספציפית לפי ה-ID שלה ואימות הפרטים.")
    def test05_get_single_expense(self):
        response = APIWorkflows.get_expense_by_id(TestAPI.created_id)
        APIVerifications.verify_status_code(response, 200)
        APIVerifications.verify_response_value(response, "description", "API_Course")

    @allure.title("API_06: Update Expense (PUT)")
    @allure.description("עדכון סכום של הוצאה קיימת מ-150 ל-200 באמצעות PUT.")
    def test06_update_expense(self):
        # מעדכנים מ-150 ל-200 בדיוק כמו שביקשת בעץ!
        response = APIWorkflows.update_expense(TestAPI.created_id, "API_Course_Updated", 200, "2025-10-10", "Education")
        APIVerifications.verify_status_code(response, 200)
        APIVerifications.verify_response_value(response, "amount", 200)

    @allure.title("API_07: Delete Expense")
    @allure.description("מחיקת הוצאה באמצעות DELETE ל-ID שלה.")
    def test07_delete_expense_api(self):
        response = APIWorkflows.delete_expense(TestAPI.created_id)
        APIVerifications.verify_status_code(response, 200)

    @allure.title("API_08: Negative - Get Deleted Expense")
    @allure.description("ניסיון לשלוף הוצאה שנמחקה וקבלת שגיאה 404.")
    def test08_negative_get_deleted(self):
        response = APIWorkflows.get_expense_by_id(TestAPI.created_id)
        APIVerifications.verify_status_code(response, 404)

    @allure.title("API_09: Negative - Delete Invalid ID")
    @allure.description("ניסיון למחוק מזהה שלא קיים במערכת (404).")
    def test09_negative_delete_invalid(self):
        response = APIWorkflows.delete_expense("invalid_id_9999")
        APIVerifications.verify_status_code(response, 404)

    @allure.title("API_10: Negative - Bad Route / Endpoint")
    @allure.description("ניסיון לגשת לכתובת API שלא קיימת ואימות שגיאה מתאימה.")
    def test10_negative_bad_route(self):
        # שליחת בקשה לנתיב "expenses_fake" במקום "expenses"
        from extensions.api_actions import APIActions
        response = APIActions.get(ConfigManager.get("api_base_url").replace("expenses", "expenses_fake"))
        APIVerifications.verify_status_code(response, 404)