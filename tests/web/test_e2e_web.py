import allure
import pytest
import time
from workflows.web.web_workflows import WebWorkflows
from extensions.ui_actions import UIActions
from extensions.web_verification import WebVerify
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from utils.logger import Logger
from config.config import ConfigManager



@allure.title("E2E: Complete Expense Lifecycle")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.usefixtures("web_setup")
class TestE2ELifecycleEnhanced:
    def test11_e2e_complete_lifecycle_enhanced(self):
        log = Logger()
        expense_name     = f"E2E_Lifecycle_{int(time.time())}"
        expense_amount   = 777
        expense_category = "Education"
        expense_date     = "2025-07-01"

        # ── BASELINE ──────────────────────────────────────────
        with allure.step("Step 1: Baseline"):
            initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()
            allure.attach(self.page.screenshot(), name="01_Baseline", attachment_type=allure.attachment_type.PNG)

        # ── CREATE ────────────────────────────────────────────
        with allure.step(f"Step 2: Create '{expense_name}'"):
            t0 = time.time()
            WebWorkflows.create_expense(self.page, description=expense_name,
                                        amount=expense_amount, category=expense_category, date=expense_date)
            self.page.wait_for_function(
                f"document.querySelectorAll('{ExpenseTrackerPage.expense_name_items}').length > {initial_count}",
                timeout=5000)
            creation_time = time.time() - t0
            allure.attach(self.page.screenshot(), name="02_After_Creation", attachment_type=allure.attachment_type.PNG)
            log.info(f"Created in {creation_time:.3f}s")

        # ── VERIFY CREATION ───────────────────────────────────
        with allure.step("Step 3: Verify creation"):
            last = self.page.locator(ExpenseTrackerPage.expense_name_items).last
            last.wait_for(state="visible", timeout=5000)

            WebVerify.contain_text(last, expense_name)
            WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_amount_items).last, str(expense_amount))
            WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_date_items).last, expense_date)
            WebVerify.contain_text(self.page.locator(ExpenseTrackerPage.expense_category_items).last, expense_category.lower())

            assert self.page.locator(ExpenseTrackerPage.expense_name_items).count() == initial_count + 1
            assert self.page.locator(ExpenseTrackerPage.expense_name_items).all_inner_texts()[-1] == expense_name

        # ── PERSISTENCE ───────────────────────────────────────
        with allure.step("Step 4: Persistence after reload"):
            self.page.reload()
            self.page.wait_for_load_state("networkidle")
            assert expense_name in self.page.locator(ExpenseTrackerPage.expense_name_items).all_inner_texts()
            allure.attach(self.page.screenshot(), name="03_After_Reload", attachment_type=allure.attachment_type.PNG)

        # ── DELETE ────────────────────────────────────────────
        with allure.step(f"Step 5: Delete '{expense_name}'"):
            t0 = time.time()
            UIActions.click(self.page, ExpenseTrackerPage.delete_buttons, is_last=True)
            self.page.wait_for_function(
                f"document.querySelectorAll('{ExpenseTrackerPage.expense_name_items}').length === {initial_count}",
                timeout=5000)
            deletion_time = time.time() - t0
            allure.attach(self.page.screenshot(), name="04_After_Deletion", attachment_type=allure.attachment_type.PNG)
            log.info(f"Deleted in {deletion_time:.3f}s")

        # ── VERIFY DELETION ───────────────────────────────────
        with allure.step("Step 6: Verify deletion"):
            assert self.page.locator(ExpenseTrackerPage.expense_name_items).count() == initial_count
            assert expense_name not in self.page.locator(ExpenseTrackerPage.expense_name_items).all_inner_texts()

        # ── PERFORMANCE ───────────────────────────────────────
        with allure.step("Step 7: Performance"):
            total_time = creation_time + deletion_time
            report = f"Creation: {creation_time:.3f}s | Deletion: {deletion_time:.3f}s | Total: {total_time:.3f}s"
            allure.attach(report, name="Performance Report", attachment_type=allure.attachment_type.TEXT)
            log.info(report)
            perf_cfg = ConfigManager.get_performance_config()
            assert creation_time < perf_cfg["max_creation_time"]
            assert deletion_time < perf_cfg["max_deletion_time"]
            
            
            
            
