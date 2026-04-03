import allure
import pytest
import time
from workflows.web.web_workflows_expense import WebWorkflows
from extensions.web_verification import WebVerify
from page_objects.web.expense_tracker_page import ExpenseTrackerPage

@allure.title("E2E: Complete Expense Lifecycle")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.usefixtures("web_setup")
class TestE2ELifecycleWeb:

    def test_e2e_complete_lifecycle_bulletproof(self):
        # 1. Data Setup
        expense = {
            "name": f"E2E_Test_{int(time.time())}",
            "amount": "777",
            "category": "Education",
            "date": "2025-07-01"
        }
        expense_created = False

        try:
            # ── BASELINE ──────────────────────────────────────────
            with allure.step("Step 1: Get initial state"):
                # שימוש בפונקציית העזר כדי לשמור על רמת אבסטרקציה גבוהה
                initial_count = WebVerify.get_elements_count(self.page, ExpenseTrackerPage.expense_name_items)

            # ── CREATE ────────────────────────────────────────────
            with allure.step(f"Step 2: Create expense '{expense['name']}'"):
                WebWorkflows.create_expense(
                    self.page,
                    expense_name=expense["name"],
                    amount=expense["amount"],
                    category=expense["category"],
                    date=expense["date"]
                )

                WebVerify.verify_element_count(self.page, ExpenseTrackerPage.expense_name_items, initial_count + 1)
                expense_created = True

            # ── VERIFY CREATION & UI ──────────────────────
            with allure.step("Step 3: Verify details and UI boundaries"):
                WebVerify.verify_expense_row_visible(self.page, expense["name"])
                WebVerify.verify_no_container_overflow(self.page, f"{ExpenseTrackerPage.expense_name_items} >> nth=-1")
                WebVerify.verify_expense_row_details(self.page, expense["name"], expense["amount"], expense["date"], expense["category"])

            # ── PERSISTENCE ───────────────────────────────────────
            with allure.step("Step 4: Persistence after reload"):
                self.page.reload()
                WebVerify.verify_expense_row_visible(self.page, expense["name"])

        finally:
            # ── TEARDOWN (Cleanup) ────────────────────────────────
            with allure.step("Step 5: Teardown - Safe Delete"):
                if expense_created:
                    try:
                        WebWorkflows.delete_expense_by_name(self.page, expense["name"])
                        WebVerify.verify_element_count(self.page, ExpenseTrackerPage.expense_name_items, initial_count)
                        WebVerify.verify_expense_row_hidden(self.page, expense["name"])
                    except Exception as e:
                        print(f"Teardown failed, cleanup your mess manually. Error: {e}")