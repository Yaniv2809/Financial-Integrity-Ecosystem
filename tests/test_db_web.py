import pytest
import allure
from extensions.db_actions import DBActions
from extensions.db_verifications import DBVerifications
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
from config.config import ConfigManager
from workflows.web.web_workflows import WebWorkflows
from extensions.web_verification import WebVerify
import os

# הפקודה הזו אומרת: "לך לתיקייה הנוכחית של הקובץ הזה (tests), תעלה רמה אחת למעלה (הפרויקט), ותיכנס ל-data".
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

class TestDBWeb:

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        print("\n[SETUP] Preparing DB for Web Test...")
        # 1. יצירת הטבלה ליתר ביטחון
        DBActions.execute_query(DB_PATH, "CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, expense_name TEXT, amount REAL, date TEXT, category TEXT)")
        
        # 2. ניקוי נתון ישן כדי למנוע כפילויות
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")
        
        # 3. הכנסת הנתון הספציפי שהטסט הזה צריך
        insert_query = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        DBActions.execute_query(DB_PATH, insert_query, ("Web_Course", 1500.0, "2026-02-25", "Education"))
        yield  
        print("\n[TEARDOWN] Cleaning up Web Test data...")
        # 4. ניקוי הנתון בסיום הטסט
        DBActions.execute_query(DB_PATH, "DELETE FROM expenses WHERE expense_name = 'Web_Course'")

    @allure.title("Web & DB: Inject DB data to Web UI")
    @allure.description("Reads 'Web_Course' from SQLite and injects it into the expense tracker website.")
    def test01_web_driven_by_db(self, page):
        # 1. קריאת הנתון שהכנו ב-Setup
        query = "SELECT * FROM expenses WHERE expense_name = 'Web_Course'"
        records = DBActions.execute_query(DB_PATH, query)
        DBVerifications.verify_record_count(records, expected_count=1)
        
        db_name = records[0][1]
        db_amount = str(int(records[0][2]))
        print(f"\n🚀 Pulled from DB: {db_name} - ${db_amount}")

        # 2. הזנת הנתונים לאתר דרך ה-Workflow
        page.goto(ConfigManager.get_env_data()['web_url'])
        
        WebWorkflows.create_expense(
            page=page, 
            description=db_name, 
            amount=db_amount, 
            date="2025-10-10", 
            category="Education"
        )
        
        # מחקנו פה את ה-goto המיותר ואת הלחיצה (ה-Workflow אמור ללחוץ בעצמו)!
        # הוספת השהייה קטנה של שנייה כדי שהאתר יספיק לרנדר את הנתון החדש ברשימה
        page.wait_for_timeout(1000)
        
        # 3. אימות שזה מופיע על המסך - בעזרת מחלקת ה-WebVerify שלנו!
        # תמשוך את האלמנט של הטקסט ותעביר אותו לאימות
        element_to_verify = page.locator(f"text={db_name}")
        
        # ודא ששם הפונקציה מתאים בדיוק למה שכתבת בקובץ web_verification.py שלך (לרוב זה verify_is_visible)
        WebVerify.verify_is_visible(element_to_verify)
        
        print("✅ Success! Data from DB is visible on the Web UI.")