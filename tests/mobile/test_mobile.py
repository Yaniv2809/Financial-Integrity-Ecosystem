import pytest
import os
from config.config import ConfigManager
from page_objects.mobile.expense_mobile_page import MobileExpensePage
from utils.common_ops import load_test_data

# the JSON resides under the workspace root `data/ddt`, not inside `tests`
DATA_FILE_PATH = r"C:\Users\yaniv\Desktop\Financial-Integrity-Ecosystem\data\ddt\expenses_json_data.json"

@pytest.mark.usefixtures("mobile_driver")
class TestMobileExpenseTracker:
    
    @pytest.fixture(autouse=True)
    def init_page(self):
        # ה-driver כבר מאותחל מה-conftest ברמת ה-Class, רק מאתחלים את עמוד המובייל
        self.page = MobileExpensePage(self.driver)

    def test_tc001_verify_ui_elements(self):
        """TC-001: בדיקה שכל השדות במסך הראשי נטענים ומוצגים"""
        print(self.driver.page_source)  # הדפסת ה-XML של המסך כדי לעזור ב-Debug אם צריךv)
        assert self.page.expense_name_field.is_displayed(), "שדה שם הוצאה לא מוצג"
        assert self.page.amount_field.is_displayed(), "שדה סכום לא מוצג"
        assert self.page.date_picker.is_displayed(), "שדה בחירת תאריך לא מוצג"
        assert self.page.category_dropdown.is_displayed(), "תפריט קטגוריות לא מוצג"
        assert self.page.add_expense_button.is_displayed(), "כפתור הוספה לא מוצג"

    # שים לב: אם load_test_data שלך לא מקבלת פרמטר (וקוראת נתיב קשיח בפנים), מחק את DATA_FILE_PATH מהסוגריים
    @pytest.mark.parametrize("expense", load_test_data(DATA_FILE_PATH))
    def test_tc002_add_multiple_expenses_ddt(self, expense):
        """TC-002: הוספת מספר הוצאות מקובץ JSON - Data Driven Testing"""
        self.page.add_full_expense(
        expense["name"],
        expense["amount"],
        expense.get("category")
    )
        
        # מכיוון שלא ידוע מה קורה באפליקציה לאחר הלחיצה (מעבר מסך/ניקוי שדות),
        # ניתן להוסיף כאן Assertion שבודק לדוגמה שהשדה התנקה, או הודעת קופצת.