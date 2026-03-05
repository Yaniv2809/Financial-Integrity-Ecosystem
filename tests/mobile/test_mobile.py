import pytest
import allure
import os
from page_objects.mobile.expense_mobile_page import MobileExpensePage
from utils.common_ops import load_test_data
from extensions.mobile_verifications import MobileVerifications
from extensions.mobile_actions import MobileActions

# the JSON resides under the workspace root `data/ddt`, not inside `tests`
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "ddt", "expenses_json_data.json"
)

@allure.epic("Mobile Expense Tracker Tests")
@pytest.mark.usefixtures("mobile_driver")
class TestMobileExpenseTracker:
    
    @pytest.fixture(autouse=True)
    def init_page(self):
        # once the driver is initialized by the fixture, we can create the page object
        self.page = MobileExpensePage(self.driver)

    @allure.story("Verify UI Elements Displayed")
    @pytest.mark.smoke
    def test_tc001_verify_ui_elements(self):
        """TC-001:Test UI Elements Displayed"""
        MobileVerifications.verify_element_displayed(self.page.expense_name_field, "Expense Name Field is not displayed")
        MobileVerifications.verify_element_displayed(self.page.amount_field, "Amount Field is not displayed")
        MobileVerifications.verify_element_displayed(self.page.date_picker, "Date Picker Field is not displayed")
        MobileVerifications.verify_element_displayed(self.page.category_dropdown, "Category Dropdown is not displayed")
        MobileVerifications.verify_element_displayed(self.page.add_expense_button, "Add Expense Button is not displayed")

    # שים לב: אם load_test_data שלך לא מקבלת פרמטר (וקוראת נתיב קשיח בפנים), מחק את DATA_FILE_PATH מהסוגריים
    @allure.story("Add Multiple Expenses from JSON Data (DDT)")
    @pytest.mark.parametrize("expense", load_test_data(DATA_FILE_PATH))
    def test_tc002_add_multiple_expenses_ddt(self, expense, mobile_driver):
        """TC-002: add multiple expenses from JSON data (DDT)"""
        self.page = MobileExpensePage(mobile_driver)
        self.actions = MobileActions(mobile_driver)
        self.actions.add_full_expense(
        expense["name"],
        expense["amount"],
        expense.get("category")
    )
        MobileVerifications.verify_text(self.page.expense_name_field, "", "Expense Name Field is not cleared after adding expense")