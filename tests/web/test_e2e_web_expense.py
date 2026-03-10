import allure
import pytest
import time
from workflows.web.web_workflows_expense import WebWorkflows
from extensions.web_verification import WebVerify
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from utils.logger import Logger
from config.config import ConfigManager

@allure.title("E2E: Complete Expense Lifecycle")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.fast_browser
@pytest.mark.usefixtures("web_setup")
class TestE2ELifecycleEnhanced:
    
    def test_e2e_complete_lifecycle_enhanced(self):
        log = Logger()
        perf_cfg = ConfigManager.get_performance_config()
        
        # 1. נתוני הבדיקה (amount מוגדר מראש כמחרוזת)
        expense = {
            "name": f"E2E_Lifecycle_{int(time.time())}",
            "amount": "777",
            "category": "Education",
            "date": "2025-07-01"
        }

        # 2. לוקייטורים מרכזיים
        names_locator = self.page.locator(ExpenseTrackerPage.expense_name_items)
        specific_row = self.page.locator(ExpenseTrackerPage.expanse_list).locator(">*").filter(has_text=expense["name"]).first

        # 3. ניהול מצב וזמנים
        initial_count = 0
        times = {"creation": 0, "deletion": 0}

        try:
            # ── BASELINE ──────────────────────────────────────────
            with allure.step("Step 1: Get initial state"):
                self.page.wait_for_load_state("networkidle")
                initial_count = names_locator.count()

            # ── CREATE ────────────────────────────────────────────
            with allure.step(f"Step 2: Create expense '{expense['name']}'"):
                t0 = time.perf_counter()
                
                WebWorkflows.create_expense(
                    self.page, 
                    description=expense["name"],
                    amount=expense["amount"], 
                    category=expense["category"], 
                    date=expense["date"]
                )
                
                WebVerify.verify_element_count(names_locator, initial_count + 1)
                times["creation"] = time.perf_counter() - t0

            # ── VERIFY CREATION & UI OVERFLOW ──────────────────────
            with allure.step("Step 3: Verify details and UI boundaries"):
                WebVerify.visible(specific_row)
                WebVerify.verify_no_container_overflow(specific_row)

                WebVerify.contain_text(specific_row.locator(ExpenseTrackerPage.expense_amount_items), expense["amount"])
                WebVerify.contain_text(specific_row.locator(ExpenseTrackerPage.expense_date_items), expense["date"])
                WebVerify.contain_text(specific_row.locator(ExpenseTrackerPage.expense_category_items), expense["category"].lower())

            # ── PERSISTENCE ───────────────────────────────────────
            with allure.step("Step 4: Persistence after reload"):
                self.page.reload()
                self.page.wait_for_load_state("networkidle")
                WebVerify.visible(specific_row)

        finally:
            # ── DELETE (Cleanup) ──────────────────────────────────
            with allure.step("Step 5: Cleanup - Delete expense"):
                if specific_row.is_visible():
                    t0 = time.perf_counter()
                    specific_row.locator("button").click()
                    
                    WebVerify.verify_element_count(names_locator, initial_count)
                    WebVerify.not_visible(specific_row)
                    times["deletion"] = time.perf_counter() - t0

            # ── PERFORMANCE ───────────────────────────────────────
            with allure.step("Step 6: Performance Validation"):
                if times["creation"] and times["deletion"]:
                    log.info(f"Performance -> Creation: {times['creation']:.3f}s | Deletion: {times['deletion']:.3f}s")
                    
                    # שימוש במפתח שקיים אצלך בקובץ JSON: "max_avg_creation_time"
                    # והגדרת fallback בטוח באמצעות .get()
                    max_creation_time = perf_cfg.get("max_avg_creation_time", 5.0) 
                    
                    # מכיוון שאין לך מדד מחיקה ב-JSON, נגדיר אחד קשיח או נשתמש באותו המדד
                    max_deletion_time = perf_cfg.get("max_deletion_time", 5.0)

                    assert times["creation"] < max_creation_time, f"Creation took {times['creation']:.2f}s, exceeding {max_creation_time}s limit"
                    assert times["deletion"] < max_deletion_time, f"Deletion took {times['deletion']:.2f}s, exceeding {max_deletion_time}s limit"