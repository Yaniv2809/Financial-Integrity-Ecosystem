import pytest
import allure
from utils.common_ops import read_json_data_by_test
from data.api.api_expense_data import MASTER_API_DATA
from workflows.api.api_workflows_expense import APIWorkflows
from extensions.api_verification import APIVerifications
from extensions.api_actions import APIActions
from config.config import ConfigManager

@allure.epic("API Interface")
@allure.feature("Expense Management API")
@pytest.mark.api
@pytest.mark.usefixtures("api_setup")
class TestAPI:
    # ID is changes 
    created_id = None
    
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("API_01: Get All Expenses (Status 200)")
    @allure.description("GET all expenses and verifying receipt of a proper data set")
    def test01_get_all_expenses(self):
        #Passing self.session to the APIWorkflows method to ensure it uses the same session for the request
        response = APIWorkflows.get_all_expenses(self.session)
        APIVerifications.verify_status_code(response, 200)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("API_02: Create New Expense (Status 201)")
    @allure.description("send POST request to create a new expense and verify the response and status code.")
    def test02_create_expense_api(self):
        expense_data = read_json_data_by_test(MASTER_API_DATA, "test02")[0]
        
        response = APIWorkflows.create_expense(
            self.session, #Passing the session to ensure consistency
            expense_data["expense_name"],  
            expense_data["amount"],
            expense_data["date"],
            expense_data["category"]
        )
        
        APIVerifications.verify_status_code(response, 201)
        APIVerifications.verify_response_value(response, "expense_name", expense_data["expense_name"])
        
        TestAPI.created_id = response.json().get("id")

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("API_03: Data Driven Testing (Multiple Items)")
    @allure.description("Create multiple expenses using data driven testing with JSON file filtered by test_id.")
    @pytest.mark.parametrize("expense_data", read_json_data_by_test(MASTER_API_DATA, "test03"))
    def test03_create_multiple_expenses_api(self, expense_data):
       
        response = APIWorkflows.create_expense(
            session=self.session, #Passing the session to ensure consistency
            expense_name=expense_data["expense_name"],    
            amount=expense_data["amount"], 
            date=expense_data["date"], 
            category=expense_data["category"]
        )
        
        APIVerifications.verify_status_code(response, 201)
        APIVerifications.verify_response_value(response, "expense_name", str(expense_data["expense_name"]))
        
        #(Cleanup)
        created_id = response.json().get("id")
        if created_id:
            APIWorkflows.delete_expense(self.session, created_id)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("API_04: Get Single Expense by ID (Status 200)")
    @allure.description("GET a single expense by ID and verify status code")
    def test04_get_single_expense(self, smart_expense_id):
        response = APIWorkflows.get_expense_by_id(self.session, smart_expense_id)
        APIVerifications.verify_status_code(response, 200)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("API_05: Update Expense (PUT)")
    @allure.description("Update the amount of an existing expense from 150 to 200 using PUT")
    def test05_update_expense(self, smart_expense_id):
        response = APIWorkflows.update_expense(self.session, smart_expense_id, "API_Course_Updated", 200, "2025-10-10", "Education")
        APIVerifications.verify_status_code(response, 200)
        APIVerifications.verify_response_value(response, "amount", 200)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("API_06: Delete Expense")
    @allure.description("Delete an expense using DELETE on its ID")
    def test06_delete_expense_api(self):
        if TestAPI.created_id is not None:
            expense_id = TestAPI.created_id                                      # class
        else:
            r = APIWorkflows.create_expense(self.session, "To_Delete", 50, "2025-11-11", "Testing")   # independent
            expense_id = r.json().get("id")

        APIVerifications.verify_status_code(
            APIWorkflows.delete_expense(self.session, expense_id), 200
        )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("API_07: Negative - Get Deleted Expense")
    @allure.description("Attempting to retrieve a deleted expense and getting a 404 error")
    def test07_negative_get_deleted(self):
        if TestAPI.created_id is not None:
            expense_id = TestAPI.created_id                                           # deleted test06 (class)
        else:
            r = APIWorkflows.create_expense(self.session, "Temp_To_Delete", 100, "2025-01-01", "Testing")  # independent 
            expense_id = r.json().get("id")
            APIWorkflows.delete_expense(self.session, expense_id)                                          # delete before verify

        APIVerifications.verify_status_code(
            APIWorkflows.get_expense_by_id(self.session, expense_id), 404
        )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("API_08: Negative - Delete Invalid ID")
    @allure.description("Attempt to delete an ID that does not exist in the system (404)")
    def test08_negative_delete_invalid(self):
        response = APIWorkflows.delete_expense(self.session, "invalid_id_9999")
        APIVerifications.verify_status_code(response, 404)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("BUG: API_09: Negative - Create Expense with Missing Fields")
    @allure.description("Attempting to create an expense without required fields and validation the server returns an error")
    @pytest.mark.use_ai
    def test09_negative_create_missing_fields(self):
        response = APIWorkflows.create_expense(self.session, "", "", "", "")
        APIVerifications.verify_status_code(response, 201)
        APIVerifications.verify_response_value(response, "expense_name", "")
        # cleanup
        APIWorkflows.delete_expense(self.session, response.json().get("id"))

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("API_10: Negative - Bad Route / Endpoint")
    @allure.description("Attempt to access an API address that does not exist and appropriate error validation.")
    def test10_negative_bad_route(self):
        
        base_url = ConfigManager.get_env_data()['api_url']
        bad_url = base_url.replace("expenses", "expenses_fake")
        
        # Since you are directly addressing Actions here, the session must be passed.
        response = APIActions.get(self.session, bad_url)
        APIVerifications.verify_status_code(response, 404)