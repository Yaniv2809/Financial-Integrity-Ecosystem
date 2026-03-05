import pytest
import allure
from utils.common_ops import read_data_from_csv
import requests
from config.config import ConfigManager
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from workflows.web.web_workflows_expense import WebWorkflows
from data.web.web_data import EXPENSES_DATA_PATH
from data.web.web_data import EXPENSES_2_DATA_PATH
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
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        WebVerify.contain_text(element["name"], "Business Lunch Web")
        WebVerify.contain_text(element["amount"], "$150")
        WebVerify.contain_text(element["date"], "2025-05-20")        
        WebVerify.contain_text(element["category"], "food")

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
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        WebVerify.contain_text(element["name"],expense_data["description"]) 
        WebVerify.contain_text(element["amount"],expense_data["amount"])
        WebVerify.contain_text(element["date"], expense_data["date"])        
        WebVerify.contain_text(element["category"], expense_data["category"].lower())
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
    @allure.description("Fetches real-time EUR to USD conversion rate via API, calculates the expense, and adds it")
    def test04_verify_expense_with_api_rate(self):
        curency_api_url = ConfigManager.get_env_data()['currency_api_url']
        response = requests.get(curency_api_url)
        data = response.json()
        
        eur_rate = data['rates']['EUR'] 
        
        eur_amount = 100

        calculated_usd = round(eur_amount / eur_rate, 2) 
        
        description = f"Business Trip Paris ({eur_amount} EUR)"
        print(f"\nReal-time EUR Rate: {eur_rate}. Converted Amount: {calculated_usd} USD")
        
        WebWorkflows.create_expense(
            page=self.page, 
            description=description, 
            amount=calculated_usd, 
            category="Transportation", 
            date="2025-06-10"
        )
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        WebVerify.contain_text(element["name"], description)
        WebVerify.contain_text(element["amount"], f"${calculated_usd}")

    #5
    @allure.title("Verify negative amount input is blocked and triggers validation alert")
    @allure.description("Negative test: Tries to type -50. The UI blocks the negative input, and clicking 'Add' triggers a validation alert.")
    def test05_negative_amount_validation(self):
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        
        alert_info = WebWorkflows.validate_expense_and_alert(
            page=self.page, 
            description="Negative Test", 
            amount=-50
        )
        
        WebVerify.soft_is_true(
            alert_info["appeared"], 
            "BUG: Expected a validation alert to pop up, but it didn't!"
        )
        
        expected_alert_text = "Please enter all details for the expense."
        WebVerify.soft_strings_are_equal(
            actual=alert_info["text"], 
            expected=expected_alert_text, 
            message=f"Alert text mismatch! Expected '{expected_alert_text}', got '{alert_info['text']}'"
        )
        WebVerify.verify_element_count(self.page.locator(ExpenseTrackerPage.list_expense_rows), initial_count)
        WebVerify.soft_all()
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
    def test08_data_persistence_on_reload(self):
        unique_desc = "Persistence Expense Test"
        WebWorkflows.create_expense(self.page, description=unique_desc, amount=77)
        self.page.reload()
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, unique_desc)

    #9
    @allure.title("Verify creation of expense with empty amount is prevented")
    @allure.description("Negative test: Tries to add an expense without entering an amount and verifies it isn't added")
    def test09_empty_amount_validation(self):
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        WebWorkflows.create_expense(self.page, description="Empty Amount Test", amount="")
        WebVerify.verify_element_count(self.page.locator(ExpenseTrackerPage.expense_name_items), initial_count)

    #10
    @allure.title("AI Failure Analysis Test (Global Hook Demo)")
    @allure.description("Intentionally fails to demonstrate the global AI error analysis hook")
    @pytest.mark.use_ai
    def test10_ai_failure_analysis(self):
        self.page.locator("#non-existent-button-for-ai-test").click(timeout=2000)
        

    #11
    @allure.title("Test - Amount numeric validation")
    @allure.description("Verify that entering non-numeric value in Amount field results in empty field and triggers alert")
    def test11_amount_field_not_numeric(self):
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        expected_msg = "Please enter all details for the expense."

        # הזנת אותיות לשדה number - הדפדפן יסנן אותן והשדה יישאר ריק
        UIActions.fill_text(self.page, ExpenseTrackerPage.txt_description, "Invalid Amount Test")
        
        amount_field = self.page.locator(ExpenseTrackerPage.txt_amount)
        amount_field.click()
        amount_field.press_sequentially("eeeeee", delay=50)
        
        UIActions.fill_text(self.page, ExpenseTrackerPage.add_date, "2025-07-01")
        UIActions.select_option(self.page, ExpenseTrackerPage.category_dropdown, "Food")
        UIActions.click(self.page, ExpenseTrackerPage.btn_add)
        
        # אימות שהשדה ריק (הדפדפן סינן את האותיות)
        WebVerify.value(amount_field, "")

        # ניסיון הוספה - אמור לקפוץ alert
        self.page.once("dialog", lambda dialog: dialog.accept())
        UIActions.click(self.page, ExpenseTrackerPage.btn_add)
        
        # אימות שלא נוספה שורה
        WebVerify.verify_no_row_added(
            self.page.locator(ExpenseTrackerPage.expense_name_items),
            initial_count,
            alert_text=expected_msg
        )


    @allure.title("Test - Expense name trim validation") 
    @allure.description("Verify that entering only spaces in Expense Name triggers an error alert")
    def test12_expense_name_trim_validation(self) -> None:
        # 1. בדיקה כמה שורות יש לפני הניסיון
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        
        # 2. ניסיון להוסיף הוצאה עם רווחים בלבד בשם
        expected_alert = "Please enter all details for the expense."
        alert_result = WebWorkflows.validate_expense_and_alert(
            page=self.page, 
            description="   ",
            amount="100",
            expected_alert=expected_alert
        )
        
        # 3. אימות שה-alert הופיע עם הטקסט הנכון
        assert alert_result["appeared"], "BUG: No alert was shown for spaces-only expense name!"
        WebVerify.strings_are_equal(
            alert_result["text"], 
            expected_alert,
            f"Alert text mismatch! Got: '{alert_result['text']}'"
        )
        
        # 4. אימות שלא נוספה שורה חדשה
        WebVerify.verify_no_row_added(
            self.page.locator(ExpenseTrackerPage.expense_name_items),
            initial_count,
            alert_text=expected_alert
        )
        
    
    @allure.title("Test13: Expense Tracker Boundary DDT Validation")
    @allure.description("Boundary testing: long text, empty name, spaces-only name with DDT")
    @pytest.mark.parametrize("expense_2_data", read_data_from_csv(EXPENSES_2_DATA_PATH))
    def test13_expense_boundry_ddt(self, expense_2_data):
        expected_status = expense_2_data["status"]
        expected_alert = "Please enter all details for the expense."

        result = WebWorkflows.validate_boundary_expense(
            page=self.page,
            description=expense_2_data["description"],
            amount=expense_2_data["amount"],
            date=expense_2_data["date"],
            category=expense_2_data["category"],
            expected_status=expected_status
        )

        if expected_status == "success":
            WebVerify.soft_text(
                self.page.locator(ExpenseTrackerPage.expense_name_items).last,
                result["description"],
                f"Expected name '{result['description'][:30]}...' but got different value"
            )
            WebVerify.soft_text(
                self.page.locator(ExpenseTrackerPage.expense_amount_items).last,
                f"${expense_2_data['amount']}",
                f"Expected amount '${expense_2_data['amount']}'"
            )
            WebVerify.soft_text(
                self.page.locator(ExpenseTrackerPage.expense_category_items).last,
                f"({expense_2_data['category'].lower()})",
                f"Expected category '({expense_2_data['category'].lower()})'"
            )
            if len(result["description"]) > 50:
                WebVerify.verify_no_container_overflow(
                    self.page.locator(ExpenseTrackerPage.expense_name_items).last
                )
            WebVerify.soft_all()

        else:
            actual_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
            WebVerify.soft_is_true(
                result["alert"]["appeared"],
                f"BUG: No alert shown for invalid input: '{expense_2_data['description']}'"
            )
            WebVerify.soft_strings_are_equal(
                result["alert"]["text"],
                expected_alert,
                f"Alert text mismatch! Expected: '{expected_alert}', Got: '{result['alert']['text']}'"
            )
            WebVerify.soft_is_true(
                actual_count == result["initial_count"],
                f"BUG: Row added despite invalid input! Before: {result['initial_count']}, After: {actual_count}"
            )
            WebVerify.soft_all()