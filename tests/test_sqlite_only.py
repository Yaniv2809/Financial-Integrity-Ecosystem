import pytest
import allure
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications

DB_PATH = r"C:\Users\yaniv\Desktop\Financial-Integrity-Ecosystem\data\expense_db.db"

#this test class is for checking that our DB actions and verifications work correctly in isolation, without involving the web UI. 
#It's a sanity check for our DB layer before we integrate it with the web tests.

class TestSQLiteDB:
    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        print("\n[SETUP] Preparing the Database...")
        # here we create the table if it doesn't exist, clear it to avoid duplicates, and insert a known record for testing
        create_table_query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_name TEXT,
            amount REAL,
            date TEXT,
            category TEXT
        )
        """
        DBActions.execute_query(DB_PATH, create_table_query)
        # 2. to make sure we have a clean slate for our tests, we clear the table before starting
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses")
        # 3. insert a known record to verify in the first test
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("Laptop", 3500.0, "2026-02-25", "Education"))
        yield 
        print("\n[TEARDOWN] DB Tests completed.")



    @allure.title("DB Test 01: Verify existing expense")
    @allure.description("Queries the DB to ensure the setup data was inserted correctly.")
    def test01_verify_expense(self):
        query = "SELECT * FROM expenses WHERE expense_name = 'Laptop'"
        records = DBActions.execute_query(DB_PATH, query)
        print(f"\n Data Extracted: {records}")
        DBVerifications.verify_record_count(records, expected_count=1)
        #index: 0=id, 1=expense_name, 2=amount, 3=date, 4=category
        assert records[0][2] == 3500.0, f" Amount mismatch! Expected 3500.0, got {records[0][2]}"



    @allure.title("DB Test 02: Insert and verify new expense")
    @allure.description("Inserts a new expense and immediately verifies it in the DB.")
    def test02_insert_new_expense(self):
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("Pizza", 120.0, "2026-02-25", "Food"))
        
        select_query = "SELECT * FROM expenses WHERE expense_name = 'Pizza'"
        records = DBActions.execute_query(DB_PATH, select_query)
        
        print(f"\n New Record Extracted: {records}")
        DBVerifications.verify_record_count(records, expected_count=1)