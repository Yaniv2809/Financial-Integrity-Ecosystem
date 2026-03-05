"""
tests/mobile/test_mobile.py
============================
טסטים מובייל מלאים – Appium + Android.

ארכיטקטורה:
  • mobile_driver fixture (conftest) → self.driver
  • MobileExpensePage (POM)          → self.page
  • MobileWorkflows                  → self.wf
  • MobileVerify                     → assertions layer
  • Allure: epic / feature / story / severity על כל טסט
  • DDT: pytest.mark.parametrize מ-JSON
  • Negative tests: שדות ריקים, סכום לא תקין
"""

import os
import time
import pytest
import allure
from page_objects.mobile.expense_mobile_page import MobileExpensePage
from workflows.mobile.mobile_workflows_expense import MobileWorkflows
from extensions.mobile_verifications import MobileVerifications
from utils.common_ops import load_test_data

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "ddt", "expenses_json_data.json"
)



    # ──────────────────────────────────────────────────────────────────
    # TC-001: UI Elements
    # ──────────────────────────────────────────────────────────────────
@allure.epic("Mobile Expense Tracker Tests")
@pytest.mark.usefixtures("mobile_driver")
class TestMobileExpenseTracker:



    # ──────────────────────────────────────────────────────────────────
    # TC-003: Single expense full flow
    # ──────────────────────────────────────────────────────────────────
    @allure.title("MOB-003: Add single expense and verify in list")
    @allure.description("הוספת הוצאה בודדת (Food) ואימות שמופיעה ברשימה.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Expense Creation")
    def test_tc003_add_single_expense(self):
        with allure.step("Add 'Grocery' expense"):
            self.wf.add_expense_flow("Grocery", 80, category="Food")
        with allure.step("Verify expense visible"):
            MobileVerifications.wait_for_text(self.driver, "Grocery")

    # ──────────────────────────────────────────────────────────────────
    # TC-004: Data persistence after background
    # ──────────────────────────────────────────────────────────────────
    @allure.title("MOB-004: Data persists after app goes to background")
    @allure.description("מוסיף הוצאה, שולח לרקע 3 שניות, מאמת שהנתון נשמר.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Persistence")
    def test_tc004_data_persistence_after_background(self):
        expense_name = "PersistenceCheck"
        with allure.step("Add expense before background"):
            self.wf.add_expense_flow(expense_name, 55, category="Education")
        with allure.step("Send app to background (3s) and resume"):
            self.wf.verify_persistence_after_restart(expense_name, seconds=3)

    # ──────────────────────────────────────────────────────────────────
    # TC-005: Negative – Empty name
    # ──────────────────────────────────────────────────────────────────
    @allure.title("MOB-005 [Negative]: Submit without expense name")
    @allure.description("טסט שלילי: מנסה להוסיף הוצאה ללא שם ומאמת שהרשימה לא גדלה.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Negative / Validation")
    def test_tc005_negative_empty_name(self):
        initial_rows = len(self.page.get_all_expense_rows())

        with allure.step("Submit with empty name field"):
            self.page.fill_amount(100)
            self.page.select_date()
            self.page.tap_add()

        with allure.step("Verify list count did NOT increase"):
            time.sleep(1)
            after_rows = len(self.page.get_all_expense_rows())
            assert after_rows == initial_rows, \
                f"❌ List grew despite empty name! Before:{initial_rows} After:{after_rows}"

    # ──────────────────────────────────────────────────────────────────
    # TC-006: Negative – Empty amount
    # ──────────────────────────────────────────────────────────────────
    @allure.title("MOB-006 [Negative]: Submit without amount")
    @allure.description("טסט שלילי: מנסה להוסיף הוצאה ללא סכום ומאמת שהרשימה לא גדלה.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Negative / Validation")
    def test_tc006_negative_empty_amount(self):
        initial_rows = len(self.page.get_all_expense_rows())

        with allure.step("Submit with empty amount field"):
            self.page.fill_name("NoAmount")
            self.page.select_date()
            self.page.tap_add()

        with allure.step("Verify list count did NOT increase"):
            time.sleep(1)
            after_rows = len(self.page.get_all_expense_rows())
            assert after_rows == initial_rows, \
                f"❌ List grew despite empty amount! Before:{initial_rows} After:{after_rows}"

    # ──────────────────────────────────────────────────────────────────
    # TC-007: Category coverage
    # ──────────────────────────────────────────────────────────────────
    @allure.title("MOB-007: Add expense for each category")
    @allure.description("מוסיף הוצאה לכל קטגוריה קיימת ומאמת שהיא מופיעה ברשימה.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Category Coverage")
    @pytest.mark.parametrize("category", ["Food", "Transportation", "Education", "Accommodation"])
    def test_tc007_all_categories(self, category):
        expense_name = f"Cat_{category}"

        with allure.step(f"Add expense with category: {category}"):
            self.wf.add_expense_flow(expense_name, 10, category=category)

        with allure.step(f"Verify '{expense_name}' in list"):
            MobileVerifications.wait_for_text(self.driver, expense_name)