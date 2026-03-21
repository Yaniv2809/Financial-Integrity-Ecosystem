import allure
import pytest
import time
from workflows.web.web_workflows_expense import WebWorkflows
from extensions.db_actions import DBActions
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from config.config import ConfigManager
from utils.common_ops import read_json_data_by_test
from data.e2e.e2e_expense_data import MASTER_E2E_DATA


@allure.epic("E2E Integration")
@allure.feature("Data Integrity: Web UI → MySQL Validation")
@pytest.mark.e2e
@pytest.mark.usefixtures("web_setup", "db_setup_teardown")
class TestE2ENegativeAmount:
    """
    Negative E2E test: Web UI accepts a negative amount (known bug),
    but MySQL CHECK constraint blocks the INSERT — proving DB-level validation.
    """
    db_path = ConfigManager.get_db_path()

    @allure.title("E2E Negative: Web UI accepts negative amount → MySQL blocks INSERT")
    @allure.description(
        "Creates an expense with a negative amount (-50) on the Web UI. "
        "The UI accepts it (bug). Then attempts to INSERT the extracted data "
        "into MySQL, which rejects it via CHECK (amount >= 0) constraint."
    )
    def test01_negative_amount_blocked_by_mysql(self):
        # ── Load test data from JSON ──────────────────────────
        data = read_json_data_by_test(MASTER_E2E_DATA, "test01_negative")[0]
        expense_name = f"{data['expense_name']}_{int(time.time())}"
        expense_amount = float(data["amount"])
        expense_category = data["category"]
        expense_date = data["date"]

        # ── STEP 1: Baseline count ───────────────────────────
        with allure.step("Step 1: Capture baseline count"):
            initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()

        # ── STEP 2: Create expense with NEGATIVE amount on Web UI
        with allure.step(f"Step 2: Create expense '{expense_name}' with negative amount ({expense_amount}) on Web UI"):
            WebWorkflows.create_expense(
                page=self.page,
                expense_name=expense_name,
                amount=expense_amount,
                category=expense_category,
                date=expense_date,
            )
            self.page.wait_for_function(
                f"document.querySelectorAll('{ExpenseTrackerPage.expense_name_items}').length > {initial_count}",
                timeout=5000,
            )
            allure.attach(
                self.page.screenshot(),
                name="01_BUG_Web_Accepted_Negative_Amount",
                attachment_type=allure.attachment_type.PNG,
            )
            print(f"\n[BUG] Web UI accepted negative amount: {expense_amount}")

        # ── STEP 3: Extract data from UI elements ────────────
        with allure.step("Step 3: Extract created record data from UI elements"):
            name_selector = f"{ExpenseTrackerPage.expense_name_items} >> nth=-1"
            amount_selector = f"{ExpenseTrackerPage.expense_amount_items} >> nth=-1"
            date_selector = f"{ExpenseTrackerPage.expense_date_items} >> nth=-1"
            category_selector = f"{ExpenseTrackerPage.expense_category_items} >> nth=-1"

            ui_name = self.page.locator(name_selector).inner_text()
            ui_amount_raw = self.page.locator(amount_selector).inner_text()
            ui_date = self.page.locator(date_selector).inner_text()
            ui_category = self.page.locator(category_selector).inner_text()

            ui_amount = float(ui_amount_raw.replace("$", "").replace(",", "").strip())
            ui_category = ui_category.strip("() ")

            print(f"[UI EXTRACTED] Name: {ui_name} | Amount: {ui_amount} | Date: {ui_date} | Category: {ui_category}")
            allure.attach(
                f"Name: {ui_name}\nAmount: {ui_amount}\nDate: {ui_date}\nCategory: {ui_category}",
                name="Extracted UI Data (Negative Amount)",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Confirm the amount is indeed negative
            assert ui_amount < 0, f"Expected negative amount but got: {ui_amount}"

        # ── STEP 4: Attempt INSERT into MySQL — expect FAILURE ─
        with allure.step("Step 4: Attempt INSERT into MySQL — expect CHECK constraint violation"):
            insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"

            try:
                DBActions.execute_query(
                    self.db_path,
                    insert_query,
                    (ui_name, ui_amount, ui_date, ui_category),
                )
                # If we get here, MySQL did NOT block it — fail the test
                pytest.fail(
                    f"MySQL accepted negative amount ({ui_amount})! "
                    f"CHECK constraint (amount >= 0) did not work."
                )
            except Exception as e:
                error_msg = str(e)
                print(f"\n[PASS] MySQL blocked negative amount: {error_msg}")
                allure.attach(
                    f"Web UI Bug: Accepted negative amount {ui_amount}\n"
                    f"MySQL Response: CHECK constraint blocked the INSERT\n"
                    f"Error: {error_msg}",
                    name="Data Integrity Report",
                    attachment_type=allure.attachment_type.TEXT,
                )

        # ── STEP 5: Verify NO record in MySQL ─────────────────
        with allure.step("Step 5: Verify no record exists in MySQL with negative amount"):
            records = DBActions.execute_query(
                self.db_path,
                "SELECT * FROM expenses WHERE expense_name = ?",
                (ui_name,),
            )
            assert len(records) == 0, (
                f"Record with negative amount found in MySQL! "
                f"Expected 0 records, got {len(records)}"
            )
            print("[DB VERIFY] Confirmed: No record with negative amount in MySQL")
