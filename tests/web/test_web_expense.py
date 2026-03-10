import pytest
import allure
from utils.common_ops import read_data_from_csv_by_test
import requests
from config.config import ConfigManager
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from workflows.web.web_workflows_expense import WebWorkflows
from data.web.web_expense_data import MASTER_CSV
from extensions.ui_actions import UIActions
from extensions.web_verification import WebVerify

@allure.epic("Web UI Testing")
@allure.feature("Expense Tracker Functionality")
@pytest.mark.usefixtures("web_setup")
class TestWeb:
    #1
    @allure.title("Create a new expense via Web UI")
    @allure.description("This test verifies that a new expense can be added to the tracker")
   
    def test01_create_new_expense_web(self):
        data = read_data_from_csv_by_test(MASTER_CSV, "test01")[0]

        WebWorkflows.create_expense(
            page = self.page,
            expense_name = data["expense_name"],
            amount = data["amount"], 
            date = data["date"],
            category = data["category"]  
        )
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        WebVerify.contain_text(element["name"], str(data["expense_name"])) 
        WebVerify.contain_text(element["amount"], str(data["amount"]))
        WebVerify.contain_text(element["date"], str(data["date"]))        
        WebVerify.contain_text(element["category"], str(data["category"]).lower())
    

    #2
    @allure.title("Create multiple expenses via DDT")
    @allure.description("This test uses Data-Driven Testing to add several expenses, reading from an external CSV file")
    @pytest.mark.parametrize("expense_data", read_data_from_csv_by_test(MASTER_CSV, "test02"))
    def test02_create_multiple_expenses_ddt(self, expense_data):

        WebWorkflows.create_expense(
            page=self.page,
            expense_name=expense_data["expense_name"],
            amount=expense_data["amount"], 
            date=expense_data["date"],
            category=expense_data["category"]  
        )
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        WebVerify.contain_text(element["name"],expense_data["expense_name"]) 
        WebVerify.contain_text(element["amount"],expense_data["amount"])
        WebVerify.contain_text(element["date"], expense_data["date"])        
        WebVerify.contain_text(element["category"], expense_data["category"].lower())
    #3
    @allure.title("Verify expense list count")
    @allure.description("This test verifies that adding new expenses properly increases the total number of items in the DOM")
    def test03_verify_expense_list_count(self):
        expenses = read_data_from_csv_by_test(MASTER_CSV, "test03")
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        print(f"\nCurrent expenses count: {initial_count}")

        for expense in expenses:
            WebWorkflows.create_expense(
                page=self.page,
                expense_name=expense["expense_name"],
                amount=expense["amount"],
                date=expense["date"],
                category=expense["category"]
            )

        expected_new_count = initial_count + len(expenses)
        WebVerify.verify_element_count(
            self.page.locator(ExpenseTrackerPage.expense_name_items), expected_new_count
        )

    #4
    @allure.title("Verify expense creation with real-time API conversion")
    @allure.description("Fetches real-time EUR to USD conversion rate via API, calculates the expense, and adds it")
    def test04_verify_expense_with_api_rate(self):
        test_data = read_data_from_csv_by_test(MASTER_CSV, "test04")[0]

        # שליפת שער חליפין בזמן אמת
        currency_api_url = ConfigManager.get_env_data()['currency_api_url']
        response = requests.get(currency_api_url)
        data = response.json()
        eur_rate = data['rates']['EUR']

        # חישוב המרה
        eur_amount = float(test_data["amount"])
        calculated_usd = round(eur_amount / eur_rate, 2)

        expense_name = f"{test_data['expense_name']} ({eur_amount:.0f} EUR)"
        print(f"\nReal-time EUR Rate: {eur_rate}. Converted Amount: {calculated_usd} USD")

        # יצירת ההוצאה
        WebWorkflows.create_expense(
            page=self.page,
            expense_name=expense_name,
            amount=calculated_usd,
            category=test_data["category"],
            date=test_data["date"]
        )

        # אימות
        element = ExpenseTrackerPage.get_last_expense_elements(self.page)
        WebVerify.contain_text(element["name"], expense_name)
        WebVerify.contain_text(element["amount"], f"${calculated_usd}")

    #5
    @allure.title("BUG: Verify negative amount input is accepted (should be blocked)")
    @allure.description("Negative test: System accepts -50 as valid amount - this is a bug. "
                        "Expected: validation alert. Actual: expense is created.")
    def test05_negative_amount_validation(self):
        data = read_data_from_csv_by_test(MASTER_CSV, "test05")[0]
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()

        WebWorkflows.create_expense(
            page=self.page,
            expense_name=data["expense_name"],
            amount=data["amount"],
            date=data["date"],
            category=data["category"]
        )

        actual_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()

        if actual_count > initial_count:
            # expense added = Bug
            print(f"\n[BUG FOUND] Negative amount '{data['amount']}' was accepted!")
            print(f"[BUG] Rows before: {initial_count}, after: {actual_count}")
            element = ExpenseTrackerPage.get_last_expense_elements(self.page)
            actual_amount = element["amount"].inner_text()
            print(f"[BUG] Amount displayed: {actual_amount}")
            pytest.fail(
                f"BUG: Negative amount '{data['amount']}' was accepted and added to the list. "
                f"Amount displayed: {actual_amount}. Expected: validation alert blocking the input."
            )
        else:
            # הרשומה לא נוספה — המערכת חסמה, זה תקין
            print(f"\n[PASS] Negative amount was correctly blocked.")

    #6
    @allure.title("Verify deletion of an expense")
    @allure.description("Adds a temporary expense, clicks its delete button, and verifies it is removed from the list")
    def test06_delete_expense(self):
        data = read_data_from_csv_by_test(MASTER_CSV, "test06")[0]
        WebWorkflows.create_expense(
            page=self.page,
            expense_name=data["expense_name"],
            amount=data["amount"],
            date=data["date"],
            category=data["category"]
        )
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
        WebWorkflows.create_expense(self.page, expense_name=long_text)
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, long_text)
        WebVerify.verify_no_container_overflow(self.page.locator(ExpenseTrackerPage.expense_name_items).last)

    #8
    @allure.title("Verify data persistence after page reload")
    @allure.description("Adds an expense, reloads the page, and verifies the expense is still displayed (checks LocalStorage)")
    def test08_data_persistence_on_reload(self):
        unique_desc = "Persistence Expense Test"
        WebWorkflows.create_expense(self.page, expense_name=unique_desc)
        self.page.reload()
        WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_name_items).last, unique_desc)

    #9
    @allure.title("Verify creation of expense with empty amount is prevented")
    @allure.description("Negative test: Tries to add an expense without entering an amount and verifies it isn't added")
    def test09_empty_amount_validation(self):
        initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
        WebWorkflows.create_expense(self.page, expense_name="Empty Amount Test", amount="")
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
        UIActions.fill_text(self.page, ExpenseTrackerPage.expense_name, "Invalid Amount Test")
        
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
            expense_name="   ",
            amount="100"
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
    @pytest.mark.parametrize("expense_2_data", read_data_from_csv_by_test(MASTER_CSV, "test13"))
    def test13_expense_boundry_ddt(self, expense_2_data):
        expected_status = expense_2_data["status"]
        expected_alert = "Please enter all details for the expense."

        result = WebWorkflows.validate_boundary_expense(
            page=self.page,
            expense_name=expense_2_data["expense_name"],
            amount=expense_2_data["amount"],
            date=expense_2_data["date"],
            category=expense_2_data["category"],
            expected_status=expected_status
        )

        if expected_status == "success":
            WebVerify.soft_text(
                self.page.locator(ExpenseTrackerPage.expense_name_items).last,
                result["expense_name"],
                f"Expected name '{result['expense_name'][:30]}...' but got different value"
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
            if len(result["expense_name"]) > 50:
                WebVerify.verify_no_container_overflow(
                    self.page.locator(ExpenseTrackerPage.expense_name_items).last
                )
            WebVerify.soft_all()

        else:
            actual_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
            WebVerify.soft_is_true(
                result["alert"]["appeared"],
                f"BUG: No alert shown for invalid input: '{expense_2_data['expense_name']}'"
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




 # @allure.title("Create a new expense via Web UI")
    # @allure.description("This test verifies that a new expense can be added to the tracker")
    # def test01_create_expense_web(self):
    #     WebWorkflows.create_expense(
    #         page=self.page,
    #         description="Business Lunch Web",
    #         amount=150,
    #         date="2025-05-20",
    #         category="Food"
    #     )
    #     element = ExpenseTrackerPage.get_last_expense_elements(self.page)
    #     WebVerify.contain_text(element["name"], "Business Lunch Web")
    #     WebVerify.contain_text(element["amount"], "$150")
    #     WebVerify.contain_text(element["date"], "2025-05-20")        
    #     WebVerify.contain_text(element["category"], "food")