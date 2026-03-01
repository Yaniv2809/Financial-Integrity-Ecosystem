import pytest
import allure
import requests
from utils.ai import get_ai_error_analysis
from utils.common_ops import read_data_from_csv
from config.config import ConfigManager
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from workflows.web.web_workflows import WebWorkflows
from data.web.web_data import EXPENSES_DATA_PATH
from extensions.ui_actions import UIActions
from extensions.web_verification import WebVerify

@allure.epic("Web UI Testing")
@allure.feature("Expense Tracker Functionality")
@pytest.mark.usefixtures("web_setup")
class TestWeb:

    #1
    @allure.title("Create a new expense via Web UI")
    @allure.description("This test verifies that a new expense can be added to the tracker")
    def test01_create_expense_web(self):
        WebWorkflows.create_expense(
            page=self.page, 
            description="Business Lunch Web", 
            amount=150, 
            date="2025-05-20",
            category="Food"    
        )
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, "Business Lunch Web")
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_amount_items).last, "150")
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_date_items).last, "2025-05-20")
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_category_items).last, "food")

    #2
    @allure.title("Create multiple expenses via DDT")
    @allure.description("This test uses Data-Driven Testing to add several expenses, reading from an external CSV file")
    @pytest.mark.parametrize("expense_data", read_data_from_csv(EXPENSES_DATA_PATH))
    def test02_create_multiple_expenses_ddt(self, expense_data):

        WebWorkflows.create_expense(
            page=self.page,
            description=expense_data["description"],
            amount=expense_data["amount"], 
            date=expense_data["date"],
            category=expense_data["category"]  
        )
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, expense_data["description"])
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_amount_items).last, expense_data["amount"])
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_date_items).last, expense_data["date"])
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_category_items).last, expense_data["category"].lower()) 
    
    #3
    @allure.title("Verify expense list count")
    @allure.description("This test verifies that adding new expenses properly increases the total number of items in the DOM")
    def test03_verify_expense_list_count(self):

        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        print(f"\nCurrent expenses count: {initial_count}")
        
        WebWorkflows.create_expense(self.page, description="Coffee", amount=15, category="Food", date="2025-06-01")
        WebWorkflows.create_expense(self.page, description="Bus ticket", amount=10, category="Transportation", date="2025-06-02")

        expected_new_count = initial_count + 2
        WebVerify.verify_element_count(self.page.locator(ExpenseTrackerPage.expense_name_items), expected_new_count)
        print(f"Verified new count is exactly: {expected_new_count}")

    #4
    @allure.title("Verify expense creation with real-time API conversion")
    @allure.description("Fetches real-time USD to ILS conversion rate via API, calculates the expense, and adds it via UI")
    def test04_verify_expense_with_api_rate(self):
        curency_api_url = ConfigManager.get_env_data()['currency_api_url']
        response = requests.get(curency_api_url)
        data = response.json()
        
        ils_rate = data['rates']['ILS']
        
        usd_amount = 100
        calculated_ils = round(usd_amount * ils_rate, 2)
        
        description = f"Business Trip NY ({usd_amount} USD)"
        print(f"\nReal-time ILS Rate: {ils_rate}. Converted Amount: {calculated_ils} ILS")
        
        WebWorkflows.create_expense(
            page=self.page, 
            description=description, 
            amount=calculated_ils, 
            category="Transportation", 
            date="2025-06-10"
        )
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, description)
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_amount_items).last, str(calculated_ils))

    #5
    @allure.title("Verify creation of expense with negative amount is prevented")
    @allure.description("Negative test: Tries to add an expense with a negative amount (-50) and verifies it fails or isn't added")
    def test05_negative_amount_validation(self):
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        WebWorkflows.create_expense(self.page, description="Negative Test", amount=-50)
        WebVerify.verify_element_count(self.page.locator(ExpenseTrackerPage.expense_name_items), initial_count)

    #6
    @allure.title("Verify deletion of an expense")
    @allure.description("Adds a temporary expense, clicks its delete button, and verifies it is removed from the list")
    def test06_delete_expense(self):
        expense_name = "To Be Deleted"
        WebWorkflows.create_expense(self.page, description=expense_name, amount=99)
        count_before_delete = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        print(f"\nCount before delete: {count_before_delete}")
        UIActions.click(self.page, ExpenseTrackerPage.delete_buttons, is_last=True)
        expected_count_after = count_before_delete - 1
        WebVerify.verify_element_count(self.page.locator(ExpenseTrackerPage.expense_name_items), expected_count_after)
        print(f"Count after delete verified as: {expected_count_after}")


    #7
    @allure.title("Verify creation of expense with a very long description")
    @allure.description("Boundary test: Adds an expense with a 100-character description to ensure the UI handles it correctly")
    def test07_long_description_boundary(self):
        long_text = "Test" * 25
        WebWorkflows.create_expense(self.page, description=long_text, amount=100)
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, long_text)
        WebVerify.verify_no_container_overflow(self.page.locator(ExpenseTrackerPage.expense_name_items).last)

    #8
    @allure.title("Verify data persistence after page reload")
    @allure.description("Adds an expense, reloads the page, and verifies the expense is still displayed (checks LocalStorage)")
    def test08_data_persistence_on_reload(self, page):
        unique_desc = "Persistence Expense Test"
        WebWorkflows.create_expense(self.page, description=unique_desc, amount=77)
        self.page.reload()
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, unique_desc)

    #9
    @allure.title("Verify creation of expense with empty amount is prevented")
    @allure.description("Negative test: Tries to add an expense without entering an amount and verifies it isn't added")
    def test09_empty_amount_validation(self, page):
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        WebWorkflows.create_expense(self.page, description="Empty Amount Test", amount="")
        WebVerify.verify_element_count(self.page.locator(ExpenseTrackerPage.expense_name_items), initial_count)

    #10
    @allure.title("AI Failure Analysis Test")
    @allure.description("Intentionally fails to demonstrate REAL AI error analysis using Groq/Llama3")
    def test10_ai_failure_analysis(self):
        try:
            # looking for a non-existent element to trigger an error
            self.page.locator("#non-existent-button").click(timeout=2000)
            
        except Exception as e:
            error_str = str(e)
            print("\n Sending error to Groq AI for analysis... please wait...")
            
            #  sending the error message to AI 
            ai_explanation = get_ai_error_analysis(error_str)
            
            # printing the AI analysis in a clear format
            print("=========================================")
            print(ai_explanation)
            print("=========================================")
            
            #Allure
            allure.attach(ai_explanation, name="Groq AI Failure Analysis", attachment_type=allure.attachment_type.TEXT)
            
            # re-raise the original exception to ensure the test is marked as failed
            raise e