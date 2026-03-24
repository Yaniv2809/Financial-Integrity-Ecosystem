import allure
import pytest
import time
from workflows.web.web_workflows_expense import WebWorkflows
from extensions.db_actions import DBActions
from extensions.web_verification import WebVerify
from extensions.db_verifications import DBVerifications
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from config.config import ConfigManager
from utils.common_ops import read_json_data_by_test
from data.e2e.e2e_expense_data import MASTER_E2E_DATA


@allure.epic("E2E Integration")
@allure.feature("Data Integrity: Web UI → MySQL Validation / Boundary")
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
    @pytest.mark.use_ai
    def test01_negative_amount_blocked_by_mysql(self):
        # ── Load test data from JSON ──────────────────────────
        data = read_json_data_by_test(MASTER_E2E_DATA, "test01_negative")[0]
        expense_name = f"{data['expense_name']}_{int(time.time())}"
        expense_amount = float(data["amount"])
        expense_category = data["category"]
        expense_date = data["date"]

        # ── STEP 1: Baseline count ───────────────────────────
        with allure.step("Step 1: Capture baseline count"):
            initial_count = ExpenseTrackerPage.get_expenses_count(self.page)

        # ── STEP 2: Create expense with NEGATIVE amount on Web UI
        with allure.step(f"Step 2: Create expense '{expense_name}' with negative amount ({expense_amount}) on Web UI"):
            WebWorkflows.create_expense(
                page=self.page,
                expense_name=expense_name,
                amount=expense_amount,
                category=expense_category,
                date=expense_date,
            )
            WebVerify.verify_element_count(self.page, ExpenseTrackerPage.expense_name_items, initial_count + 1)
            allure.attach(
                self.page.screenshot(),
                name="01_BUG_Web_Accepted_Negative_Amount",
                attachment_type=allure.attachment_type.PNG,
            )
            print(f"\n[BUG] Web UI accepted negative amount: {expense_amount}")

        # ── STEP 3: Extract data from UI elements ────────────
        with allure.step("Step 3: Extract created record data from UI elements"):
            last_elements = ExpenseTrackerPage.get_last_expense_elements(self.page)

            ui_name = last_elements["name"].inner_text()
            ui_amount_raw = last_elements["amount"].inner_text()
            ui_date = last_elements["date"].inner_text()
            ui_category = last_elements["category"].inner_text()

            ui_amount = float(ui_amount_raw.replace("$", "").replace(",", "").strip())
            ui_category = ui_category.strip("() ")

            print(f"[UI EXTRACTED] Name: {ui_name} | Amount: {ui_amount} | Date: {ui_date} | Category: {ui_category}")
            allure.attach(
                f"Name: {ui_name}\nAmount: {ui_amount}\nDate: {ui_date}\nCategory: {ui_category}",
                name="Extracted UI Data (Negative Amount)",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Confirm the amount is indeed negative
            WebVerify.soft_is_true(ui_amount < 0, f"Expected negative amount but got: {ui_amount}")

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
            DBVerifications.verify_record_count(records, expected_count=0)
            print("[DB VERIFY] Confirmed: No record with negative amount in MySQL")

    @allure.title("E2E Boundary: 300-char expense name exceeds MySQL VARCHAR(255)")
    @allure.description(
        "Creates an expense with a 300-character name via Web UI. "
        "The UI accepts it without limit. Then attempts to INSERT into MySQL "
        "where expense_name is VARCHAR(255) — expecting truncation or rejection. "
        "Severity: Medium — silent data loss if DB truncates without error."
    )
    def test02_overflow_name_exceeds_varchar(self):
        # ── Load test data from JSON ──────────────────────────
        data = read_json_data_by_test(MASTER_E2E_DATA, "test02_overflow_name")[0]
        name_length = int(data["expense_name_length"])
        long_name = f"Overflow_{'X' * (name_length - len('Overflow_'))}_{int(time.time())}"
        expense_amount = float(data["amount"])
        expense_category = data["category"]
        expense_date = data["date"]

        print(f"\n[TEST] Expense name length: {len(long_name)} chars (DB limit: VARCHAR(255))")

        # ── STEP 1: Baseline count ───────────────────────────
        with allure.step("Step 1: Capture baseline count"):
            initial_count = ExpenseTrackerPage.get_expenses_count(self.page)

        # ── STEP 2: Create expense with 300-char name on Web UI
        with allure.step(f"Step 2: Create expense with {len(long_name)}-char name on Web UI"):
            WebWorkflows.create_expense(
                page=self.page,
                expense_name=long_name,
                amount=expense_amount,
                category=expense_category,
                date=expense_date,
            )
            WebVerify.verify_element_count(self.page, ExpenseTrackerPage.expense_name_items, initial_count + 1)
            allure.attach(
                self.page.screenshot(),
                name="01_Web_Accepted_Long_Name",
                attachment_type=allure.attachment_type.PNG,
            )
            print(f"[BUG] Web UI accepted {len(long_name)}-char name without validation")

        # ── STEP 3: Extract name from UI ─────────────────────
        with allure.step("Step 3: Extract the long name from UI"):
            last_elements = ExpenseTrackerPage.get_last_expense_elements(self.page)
            ui_name = last_elements["name"].inner_text()
            print(f"[UI EXTRACTED] Name length in DOM: {len(ui_name)} chars")

        # ── STEP 4: Attempt INSERT into MySQL — VARCHAR(255) limit
        with allure.step("Step 4: Attempt INSERT into MySQL — expect VARCHAR(255) boundary issue"):
            insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
            db_error = None

            try:
                DBActions.execute_query(
                    self.db_path,
                    insert_query,
                    (ui_name, expense_amount, expense_date, expense_category),
                )
                # MySQL in strict mode will reject, in non-strict will truncate
                print("[WARNING] MySQL accepted the long name — checking for silent truncation...")
            except Exception as e:
                db_error = str(e)
                print(f"\n[PASS] MySQL rejected long name: {db_error}")

        # ── STEP 5: Verify data integrity ────────────────────
        with allure.step("Step 5: Verify data integrity — check for truncation or rejection"):
            if db_error:
                # MySQL strict mode rejected it
                allure.attach(
                    f"Web UI Bug: Accepted {len(long_name)}-char name (no client-side limit)\n"
                    f"MySQL Response: Rejected — exceeds VARCHAR(255)\n"
                    f"Error: {db_error}",
                    name="Data Integrity Report — Name Overflow",
                    attachment_type=allure.attachment_type.TEXT,
                )
                records = DBActions.execute_query(
                    self.db_path,
                    "SELECT * FROM expenses WHERE expense_name LIKE 'Overflow_%'",
                )
                DBVerifications.verify_record_count(records, expected_count=0)
                print("[DB VERIFY] Confirmed: No truncated record in MySQL")
            else:
                # MySQL non-strict mode — check if data was silently truncated
                records = DBActions.execute_query(
                    self.db_path,
                    "SELECT expense_name FROM expenses WHERE expense_name LIKE 'Overflow_%'",
                )
                if records:
                    stored_name = records[0][0]
                    stored_len = len(stored_name)
                    print(f"[RESULT] Stored name length: {stored_len} (original: {len(ui_name)})")

                    allure.attach(
                        f"Web UI Bug: Accepted {len(long_name)}-char name\n"
                        f"MySQL: Stored {stored_len} chars (silent truncation!)\n"
                        f"Data Loss: {len(ui_name) - stored_len} characters lost",
                        name="Data Integrity Report — Silent Truncation",
                        attachment_type=allure.attachment_type.TEXT,
                    )

                    if stored_len < len(ui_name):
                        pytest.fail(
                            f"SILENT DATA LOSS: MySQL truncated name from "
                            f"{len(ui_name)} to {stored_len} chars without error!"
                        )

        # ── CLEANUP ──────────────────────────────────────────
        with allure.step("Cleanup: Remove test records"):
            try:
                DBActions.execute_query(
                    self.db_path,
                    "DELETE FROM expenses WHERE expense_name LIKE 'Overflow_%'",
                )
            except Exception:
                pass
