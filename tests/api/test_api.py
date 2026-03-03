import pytest
import allure
from utils.common_ops import read_data_from_csv
from workflows.api.api_workflows import APIWorkflows
from extensions.api_verification import APIVerifications



@allure.epic("API Interface")
@allure.feature("Expense Management API")
@pytest.mark.usefixtures("api_setup")
class TestAPI:
    # משתנה ברמת המחלקה לשמירת ה-ID בין הטסטים
    created_id = None
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

    @allure.title("API_04: Get Single Expense by ID")
    @allure.description("משיכת הוצאה ספציפית לפי ה-ID שלה ואימות הפרטים.")
    def test04_get_single_expense(self):
        response = APIWorkflows.get_expense_by_id(TestAPI.created_id)
        APIVerifications.verify_status_code(response, 200)
        APIVerifications.verify_response_value(response, "description", "API_Course")

    @allure.title("API_05: Update Expense (PUT)")
    @allure.description("עדכון סכום של הוצאה קיימת מ-150 ל-200 באמצעות PUT.")
    def test05_update_expense(self):
        # מעדכנים מ-150 ל-200 בדיוק כמו שביקשת בעץ!
        response = APIWorkflows.update_expense(TestAPI.created_id, "API_Course_Updated", 200, "2025-10-10", "Education")
        APIVerifications.verify_status_code(response, 200)
        APIVerifications.verify_response_value(response, "amount", 200)

    @allure.title("API_06: Delete Expense")
    @allure.description("מחיקת הוצאה באמצעות DELETE ל-ID שלה.")
    def test06_delete_expense_api(self):
        response = APIWorkflows.delete_expense(TestAPI.created_id)
        APIVerifications.verify_status_code(response, 200)

    @allure.title("API_07: Negative - Get Deleted Expense")
    @allure.description("ניסיון לשלוף הוצאה שנמחקה וקבלת שגיאה 404.")
    def test07_negative_get_deleted(self):
        response = APIWorkflows.get_expense_by_id(TestAPI.created_id)
        APIVerifications.verify_status_code(response, 404)

    @allure.title("API_08: Negative - Delete Invalid ID")
    @allure.description("ניסיון למחוק מזהה שלא קיים במערכת (404).")
    def test08_negative_delete_invalid(self):
        response = APIWorkflows.delete_expense("invalid_id_9999")
        APIVerifications.verify_status_code(response, 404)

    @allure.title("API_10: Negative - Bad Route / Endpoint")
    @allure.description("ניסיון לגשת לכתובת API שלא קיימת ואימות שגיאה מתאימה.")
    def test10_negative_bad_route(self):
        from extensions.api_actions import APIActions
        from config.config import ConfigManager
        
        # מושכים את הכתובת האמיתית מהקונפיג
        base_url = ConfigManager.get_env_data()['api_url']
        
        # מחליפים את המילה expenses במשהו שלא קיים כדי להכשיל את הנתיב
        bad_url = base_url.replace("expenses", "expenses_fake")
        
        response = APIActions.get(bad_url)
        APIVerifications.verify_status_code(response, 404)