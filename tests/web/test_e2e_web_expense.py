import allure
import pytest
import time
from playwright.sync_api import expect
from workflows.web.web_workflows_expense import WebWorkflows
from extensions.web_verification import WebVerify
from page_objects.web.expense_tracker_page import ExpenseTrackerPage

@allure.title("E2E: Complete Expense Lifecycle")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
# @pytest.mark.fast_browser
@pytest.mark.usefixtures("web_setup")
class TestE2ELifecycleWeb:

    def test_e2e_complete_lifecycle_bulletproof(self):
        # 1. data test
        unique_id = int(time.time())
        expense = {
            "name": f"E2E_Test_{unique_id}",
            "amount": "777",
            "category": "Education",
            "date": "2025-07-01"
        }

        # 2. smart locators
        # catch the expense uniqe name
        expense_list_container = self.page.locator(ExpenseTrackerPage.expense_list)
        names_locator = self.page.locator(ExpenseTrackerPage.expense_name_items)
        specific_row = expense_list_container.locator("li").filter(has_text=expense["name"])

        # הלוקייטור הזה בטוח לשימוש כי הוא מחפש כפתור *רק* בתוך השורה הספציפית שלנו
        delete_btn = specific_row.locator("button")

        initial_count = 0
        expense_created = False

        try:
            # ── BASELINE ──────────────────────────────────────────
            with allure.step("Step 1: Get initial state without networkidle"):
                # Playwright ממתין אוטומטית עד שהרשימה זמינה
                initial_count = names_locator.count()

            # ── CREATE ────────────────────────────────────────────
            with allure.step(f"Step 2: Create expense '{expense['name']}'"):
                WebWorkflows.create_expense(
                    self.page,
                    expense_name=expense["name"],
                    amount=expense["amount"],
                    category=expense["category"],
                    date=expense["date"]
                )

                # ה-expect המובנה ימתין אוטומטית שהשורה תתווסף
                expect(names_locator).to_have_count(initial_count + 1, timeout=3000)
                expense_created = True

            # ── VERIFY CREATION & UI ──────────────────────
            with allure.step("Step 3: Verify details and UI boundaries"):
                # מוודא שהשורה באמת נוצרה ומוצגת
                expect(specific_row).to_be_visible()

                # בודק חריגות UI לפי הפונקציה שלך
                WebVerify.verify_no_container_overflow(self.page, f"{ExpenseTrackerPage.expense_name_items} >> nth=-1")

                # מוודא שהנתונים נכונים
                expect(specific_row.locator(ExpenseTrackerPage.expense_amount_items)).to_contain_text(expense["amount"])
                expect(specific_row.locator(ExpenseTrackerPage.expense_date_items)).to_contain_text(expense["date"])
                expect(specific_row.locator(ExpenseTrackerPage.expense_category_items)).to_contain_text(expense["category"].lower())

            # ── PERSISTENCE ───────────────────────────────────────
            with allure.step("Step 4: Persistence after reload"):
                self.page.reload()
                # מחכים שהשורה הספציפית תחזור להיות גלויה - מוכיח שהשמירה עבדה
                expect(specific_row).to_be_visible()

        finally:
            # ── TEARDOWN (Cleanup) ────────────────────────────────
            # זה חייב לקרות בכל מצב, אבל לא להכשיל את הטסט או לדרוס שגיאה מקורית
            with allure.step("Step 5: Teardown - Safe Delete"):
                if expense_created:
                    try:
                        delete_btn.click(timeout=3000)
                        expect(names_locator).to_have_count(initial_count, timeout=3000)
                        expect(specific_row).not_to_be_visible()
                    except Exception as e:
                        # אנחנו בולעים את השגיאה של ה-Teardown כדי שהטסט יראה את הנפילה האמיתית אם הייתה כזו ב-try
                        print(f"Teardown failed, cleanup your mess manually. Error: {e}")
