import allure
import pytest
import time
import os
import requests
from workflows.web.web_workflows_expense import WebWorkflows
from extensions.api_actions import APIActions
from extensions.api_verification import APIVerifications
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from config.config import ConfigManager
from utils.common_ops import calc_performance




@allure.epic("E2E Integration")
@allure.feature("Web UI → API + DB")
@pytest.mark.e2e
@pytest.mark.usefixtures("web_setup", "db_setup_teardown")
class TestE2EWebApiDb:
    """
    E2E test: creates a record via the Web UI, extracts displayed data from UI elements,
    then simultaneously inserts it into the JSON server (api_url) and SQLite DB.
    """
    db_path = ConfigManager.get_db_path()
    @allure.title("E2E: Web UI → Extract Data → Insert to API + DB")
    @allure.description(
        "Creates an expense on the web UI, reads it back from the DOM elements, "
        "then POSTs to JSON server and INSERTs to SQLite using the extracted data."
    )
    def test01_web_to_api_and_db(self):
        api_url = ConfigManager.get_env_data()["api_url"]
        expense_name = f"E2E_Web2All_{int(time.time())}"
        expense_amount = 555
        expense_category = "Education"
        expense_date = "2026-05-15"
        api_id = None
        perf_api_ids = []
        perf_db_names = []

        try:
            # ── STEP 1: Baseline count ───────────────────────────
            with allure.step("Step 1: Capture baseline count"):
                initial_count = self.page.locator(ExpenseTrackerPage.expense_name_items).count()

            # ── STEP 2: Create expense on Web UI ─────────────────
            with allure.step(f"Step 2: Create expense '{expense_name}' on Web UI"):
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
                    name="01_After_Web_Creation",
                    attachment_type=allure.attachment_type.PNG,
                )

            # ── STEP 3: Extract data from UI elements ────────────
            with allure.step("Step 3: Extract created record data from UI elements"):
                ui_name = self.page.locator(ExpenseTrackerPage.expense_name_items).last.inner_text()
                ui_amount_raw = self.page.locator(ExpenseTrackerPage.expense_amount_items).last.inner_text()
                ui_date = self.page.locator(ExpenseTrackerPage.expense_date_items).last.inner_text()
                ui_category = self.page.locator(ExpenseTrackerPage.expense_category_items).last.inner_text()

                # Parse amount: strip '$' prefix and convert to float
                ui_amount = float(ui_amount_raw.replace("$", "").strip())

                # Parse category: strip parentheses from UI display (e.g. "(education)" → "education")
                ui_category = ui_category.strip("() ")

                print(f"\n[UI EXTRACTED] Name: {ui_name} | Amount: {ui_amount} | Date: {ui_date} | Category: {ui_category}")
                allure.attach(
                    f"Name: {ui_name}\nAmount: {ui_amount}\nDate: {ui_date}\nCategory: {ui_category}",
                    name="Extracted UI Data",
                    attachment_type=allure.attachment_type.TEXT,
                )

            # ── STEP 4: POST extracted data to JSON server ───────
            with allure.step("Step 4: POST extracted data to JSON server (api_url)"):
                api_payload = {
                    "expense_name": ui_name,
                    "amount": ui_amount,
                    "date": ui_date,
                    "category": ui_category,
                }
                api_response = APIActions.post(api_url, api_payload)
                APIVerifications.verify_status_code(api_response, 201)
                api_id = api_response.json().get("id")
                print(f"[API] Created record with ID: {api_id}")

            # ── STEP 5: INSERT extracted data to SQLite DB ───────
            with allure.step("Step 5: INSERT extracted data to SQLite DB"):
                insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
                DBActions.execute_query(self.db_path, insert_query, (ui_name, ui_amount, ui_date, ui_category))
                print(f"[DB] Inserted record: {ui_name}")

            # ── STEP 6: Verify API record ────────────────────────
            with allure.step("Step 6: Verify record exists in JSON server"):
                get_response = APIActions.get(f"{api_url}/{api_id}")
                APIVerifications.verify_status_code(get_response, 200)
                api_data = get_response.json()
                assert api_data["expense_name"] == ui_name, f"API name mismatch: {api_data['expense_name']} != {ui_name}"
                assert api_data["amount"] == ui_amount, f"API amount mismatch: {api_data['amount']} != {ui_amount}"
                print("[API VERIFY] Record confirmed in JSON server")

            # ── STEP 7: Verify DB record ─────────────────────────
            with allure.step("Step 7: Verify record exists in SQLite DB"):
                records = DBActions.execute_query(
                    self.db_path,
                    "SELECT expense_name, amount, date, category FROM expenses WHERE expense_name = ?",
                    (ui_name,),
                )
                DBVerifications.verify_record_count(records, expected_count=1)
                assert records[0][0] == ui_name, f"DB name mismatch: {records[0][0]} != {ui_name}"
                assert records[0][1] == ui_amount, f"DB amount mismatch: {records[0][1]} != {ui_amount}"
                assert records[0][2] == ui_date, f"DB date mismatch: {records[0][2]} != {ui_date}"
                print("[DB VERIFY] Record confirmed in SQLite")

            # ── STEP 8: Performance - Multiple Iterations ────────
            with allure.step("Step 8: Performance test (10 iterations)"):
                perf_cfg = ConfigManager.get_performance_config()
                api_times = []
                db_times = []

                for i in range(10):
                    iter_name = f"Perf_Test_{int(time.time())}_{i}"

                    # Time API POST
                    t0 = time.time()
                    resp = APIActions.post(api_url, {
                        "expense_name": iter_name,
                        "amount": ui_amount,
                        "date": ui_date,
                        "category": ui_category,
                    })
                    api_times.append(time.time() - t0)
                    perf_api_ids.append(resp.json().get("id"))

                    # Time DB INSERT
                    t0 = time.time()
                    DBActions.execute_query(
                        self.db_path,
                        "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)",
                        (iter_name, ui_amount, ui_date, ui_category),
                    )
                    db_times.append(time.time() - t0)
                    perf_db_names.append(iter_name)

                # Calculate performance stats
                api_perf = calc_performance(api_times)
                db_perf = calc_performance(db_times)

                report = (
                    f"API Performance (10 iterations):\n"
                    f"  Avg: {api_perf['avg']:.4f}s | P95: {api_perf['p95']:.4f}s | "
                    f"Min: {api_perf['min']:.4f}s | Max: {api_perf['max']:.4f}s | "
                    f"Degradation: {api_perf['degradation']*100:.1f}%\n"
                    f"DB Performance (10 iterations):\n"
                    f"  Avg: {db_perf['avg']:.4f}s | P95: {db_perf['p95']:.4f}s | "
                    f"Min: {db_perf['min']:.4f}s | Max: {db_perf['max']:.4f}s | "
                    f"Degradation: {db_perf['degradation']*100:.1f}%"
                )
                print(f"\n[PERFORMANCE]\n{report}")
                allure.attach(report, name="Performance Report", attachment_type=allure.attachment_type.TEXT)

                # Assertions
                assert api_perf["avg"] < perf_cfg["max_avg_creation_time"], \
                    f"API avg {api_perf['avg']:.3f}s exceeds max {perf_cfg['max_avg_creation_time']}s"
                assert api_perf["p95"] < perf_cfg["max_p95_time"], \
                    f"API p95 {api_perf['p95']:.3f}s exceeds max {perf_cfg['max_p95_time']}s"
                assert db_perf["avg"] < perf_cfg["max_avg_creation_time"], \
                    f"DB avg {db_perf['avg']:.3f}s exceeds max {perf_cfg['max_avg_creation_time']}s"
                assert db_perf["p95"] < perf_cfg["max_p95_time"], \
                    f"DB p95 {db_perf['p95']:.3f}s exceeds max {perf_cfg['max_p95_time']}s"


        # finally:
        #     pass
        finally:
            # ── CLEANUP ──────────────────────────────────────────
            if api_id:
                requests.delete(f"{api_url}/{api_id}")
                print(f"[CLEANUP] Deleted API record ID: {api_id}")
            DBActions.execute_query(
                self.db_path,
                "DELETE FROM expenses WHERE expense_name = ?",
                (expense_name,),
            )
            # Cleanup performance iteration records
            for pid in perf_api_ids:
                try:
                    requests.delete(f"{api_url}/{pid}")
                except Exception:
                    pass
            for pname in perf_db_names:
                try:
                    DBActions.execute_query(self.db_path, "DELETE FROM expenses WHERE expense_name = ?", (pname,))
                except Exception:
                    pass
            print("[CLEANUP] Deleted all records (main + 10 perf iterations)")
