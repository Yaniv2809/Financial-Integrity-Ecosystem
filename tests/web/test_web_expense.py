import pytest
import allure
import requests
from utils.common_ops import read_data_from_csv_by_test
from config.config import ConfigManager
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from workflows.web.web_workflows_expense import WebWorkflows
from data.web.web_expense_data import MASTER_CSV
from extensions.ui_actions import UIActions
from extensions.web_verification import WebVerify

@allure.epic("Web UI Testing")
@allure.feature("Expense Tracker Functionality")
@pytest.mark.web
@pytest.mark.usefixtures("web_setup")
class TestWeb:
    
    # 1
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Create a new expense via Web UI")
    @allure.description("This test verifies that a new expense can be added to the tracker")
    def test01_create_new_expense_web(self):
        data = read_data_from_csv_by_test(MASTER_CSV, "test01")[0]

        WebWorkflows.create_expense(
            page=self.page,
            expense_name=data["expense_name"],
            amount=data["amount"], 
            date=data["date"],
            category=data["category"]  
        )
        
        # Selectors for the last added expense (using nth=-1 to target the most recent entry)
        name_selector = f"{ExpenseTrackerPage.expense_name_items} >> nth=-1"
        amount_selector = f"{ExpenseTrackerPage.expense_amount_items} >> nth=-1"
        date_selector = f"{ExpenseTrackerPage.expense_date_items} >> nth=-1"
        category_selector = f"{ExpenseTrackerPage.expense_category_items} >> nth=-1"

        WebVerify.contain_text(self.page, name_selector, str(data["expense_name"])) 
        WebVerify.contain_text(self.page, amount_selector, str(data["amount"]))
        WebVerify.contain_text(self.page, date_selector, str(data["date"]))        
        WebVerify.contain_text(self.page, category_selector, str(data["category"]).lower())
    
    # 2
    @allure.severity(allure.severity_level.CRITICAL)
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
        
        name_selector = f"{ExpenseTrackerPage.expense_name_items} >> nth=-1"
        amount_selector = f"{ExpenseTrackerPage.expense_amount_items} >> nth=-1"
        date_selector = f"{ExpenseTrackerPage.expense_date_items} >> nth=-1"
        category_selector = f"{ExpenseTrackerPage.expense_category_items} >> nth=-1"

        WebVerify.contain_text(self.page, name_selector, expense_data["expense_name"]) 
        WebVerify.contain_text(self.page, amount_selector, expense_data["amount"])
        WebVerify.contain_text(self.page, date_selector, expense_data["date"])        
        WebVerify.contain_text(self.page, category_selector, expense_data["category"].lower())
    
    # 3
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify expense list count")
    @allure.description("This test verifies that adding new expenses properly increases the total number of items in the DOM")
    def test03_verify_expense_list_count(self):
        expenses = read_data_from_csv_by_test(MASTER_CSV, "test03")
        initial_count = ExpenseTrackerPage.get_expenses_count(self.page)
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
            page=self.page, 
            selector=ExpenseTrackerPage.expense_name_items, 
            expected_count=expected_new_count
        )

    # 4
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify expense creation with real-time API conversion")
    @allure.description("Fetches real-time EUR to USD conversion rate via API, calculates the expense, and adds it")
    def test04_verify_expense_with_api_rate(self):
        test_data = read_data_from_csv_by_test(MASTER_CSV, "test04")[0]

        currency_api_url = ConfigManager.get_env_data()['currency_api_url']
        response = requests.get(currency_api_url)
        data = response.json()
        eur_rate = data['rates']['EUR']

        eur_amount = float(test_data["amount"])
        calculated_usd = round(eur_amount / eur_rate, 2)

        expense_name = f"{test_data['expense_name']} ({eur_amount:.0f} EUR)"
        print(f"\nReal-time EUR Rate: {eur_rate}. Converted Amount: {calculated_usd} USD")

        WebWorkflows.create_expense(
            page=self.page,
            expense_name=expense_name,
            amount=calculated_usd,
            category=test_data["category"],
            date=test_data["date"]
        )

        name_selector = f"{ExpenseTrackerPage.expense_name_items} >> nth=-1"
        amount_selector = f"{ExpenseTrackerPage.expense_amount_items} >> nth=-1"

        WebVerify.contain_text(self.page, name_selector, expense_name)
        WebVerify.contain_text(self.page, amount_selector, f"${calculated_usd}")

    # 5
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("BUG: Verify negative amount input is accepted (should be blocked)")
    @allure.description("Negative test: System accepts -50 as valid amount - this is a bug. Expected: validation alert. Actual: expense is created.")
    @pytest.mark.use_ai
    @pytest.mark.xfail(reason="Known Bug: UI accepts negative amounts without validation")
    def test05_negative_amount_validation(self):
        data = read_data_from_csv_by_test(MASTER_CSV, "test05")[0]
        initial_count = ExpenseTrackerPage.get_expenses_count(self.page)
        
        WebWorkflows.create_expense(
            page=self.page,
            expense_name=data["expense_name"],
            amount=data["amount"],
            date=data["date"],
            category=data["category"]
        )
        
        WebVerify.verify_element_count(
            page=self.page,
            selector=ExpenseTrackerPage.expense_name_items,
            expected_count=initial_count
        )
        
    # 6
    @allure.severity(allure.severity_level.CRITICAL)
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
        count_before_delete = ExpenseTrackerPage.get_expenses_count(self.page)
        print(f"\nCount before delete: {count_before_delete}")

        UIActions.click(self.page, ExpenseTrackerPage.delete_buttons, is_last=True)
        expected_count_after = count_before_delete - 1
        
        WebVerify.verify_element_count(
            page=self.page, 
            selector=ExpenseTrackerPage.expense_name_items, 
            expected_count=expected_count_after
        )

    # 7
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify creation of expense with a very long description")
    @allure.description("Boundary test: Adds an expense with a 100-character description to ensure the UI handles it correctly")
    @pytest.mark.xfail(reason="Known Bug: Long text overflows the expense card container")
    def test07_long_description_boundary(self):
        long_text = "Test" * 25
        WebWorkflows.create_expense(self.page, expense_name=long_text)
        
        last_item_selector = f"{ExpenseTrackerPage.expense_name_items} >> nth=-1"
        WebVerify.contain_text(self.page, last_item_selector, long_text)
        WebVerify.verify_no_container_overflow(self.page, last_item_selector)

    # 8
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify data persistence after page reload")
    @allure.description("Adds an expense, reloads the page, and verifies the expense is still displayed (checks LocalStorage)")
    def test08_data_persistence_on_reload(self):
        unique_desc = "Persistence Expense Test"
        WebWorkflows.create_expense(self.page, expense_name=unique_desc)
        self.page.reload()
        
        last_item_selector = f"{ExpenseTrackerPage.expense_name_items} >> nth=-1"
        WebVerify.contain_text(self.page, last_item_selector, unique_desc)

    # 9
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify creation of expense with empty amount is prevented")
    @allure.description("Negative test: Tries to add an expense without entering an amount and verifies it isn't added")
    def test09_empty_amount_validation(self):
        initial_count = ExpenseTrackerPage.get_expenses_count(self.page)
        WebWorkflows.create_expense(self.page, expense_name="Empty Amount Test", amount="")
        
        WebVerify.verify_element_count(
            page=self.page, 
            selector=ExpenseTrackerPage.expense_name_items, 
            expected_count=initial_count)

    # 10
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("AI Failure Analysis Test (Global Hook Demo)")
    @allure.description("Intentionally fails to demonstrate the global AI error analysis hook")
    @pytest.mark.use_ai
    @pytest.mark.xfail(reason="Intentional failure to demonstrate AI-powered error analysis")
    def test10_ai_failure_analysis(self):
        WebWorkflows.simulate_ui_failure_for_ai(self.page)
        

    #11
    # @allure.title("Test - Amount numeric validation")
    # @allure.description("Verify that entering non-numeric value in Amount field results in empty field and triggers alert")
    # def test11_amount_field_not_numeric(self):
    #     initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
    #     expected_msg = "Please enter all details for the expense."

    #     # הזנת אותיות לשדה number - הדפדפן יסנן אותן והשדה יישאר ריק
    #     UIActions.fill_text(self.page, ExpenseTrackerPage.expense_name, "Invalid Amount Test")
        
    #     amount_field = self.page.locator(ExpenseTrackerPage.txt_amount)
    #     amount_field.click()
    #     amount_field.press_sequentially("eeeeee", delay=50)
        
    #     UIActions.fill_text(self.page, ExpenseTrackerPage.add_date, "2025-07-01")
    #     UIActions.select_option(self.page, ExpenseTrackerPage.category_dropdown, "Food")
    #     UIActions.click(self.page, ExpenseTrackerPage.btn_add)
        
    #     # אימות שהשדה ריק (הדפדפן סינן את האותיות)
    #     WebVerify.value(amount_field, "")

    #     # ניסיון הוספה - אמור לקפוץ alert
    #     self.page.once("dialog", lambda dialog: dialog.accept())
    #     UIActions.click(self.page, ExpenseTrackerPage.btn_add)
        
    #     # אימות שלא נוספה שורה
    #     WebVerify.verify_no_row_added(
    #         self.page.locator(ExpenseTrackerPage.expense_name_items),
    #         initial_count,
    #         alert_text=expected_msg
    #     )
        


