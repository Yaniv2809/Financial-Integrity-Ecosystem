import pytest
import time
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

from page_objects.mobile.expense_mobile_page import MobileExpensePage
from utils.common_ops import load_test_data

# נתיב דינמי לקובץ ה-JSON
DATA_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "ddt", "expenses_json_data.json"
)


@pytest.mark.usefixtures("mobile_driver")
class TestMobileExpenseTracker:
    """
    Mobile Test Suite - ATID Expense Tracker (WebView Hybrid)
    כולל: בדיקות UI, DDT, Full Flow, מקלדת, ועקביות נתונים.
    """

    @pytest.fixture(autouse=True)
    def init_page(self):
        self.page = MobileExpensePage(self.driver)

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────
    def _add_expense(self, name: str, amount: str, day: str = None, category: str = None):
        """
        מוסיף הוצאה מלאה דרך ה-Page Object.
        :param name: שם ההוצאה
        :param amount: סכום ההוצאה
        :param day: מספר היום לבחירה בלוח השנה (אופציונלי - אם None, בוחר את היום הנוכחי)
        :param category: קטגוריה לבחירה מהתפריט (אופציונלי)
        """
        wait = WebDriverWait(self.driver, 10)

        # שם הוצאה
        self.page.expense_name_field.click()
        self.page.expense_name_field.clear()
        self.page.expense_name_field.send_keys(name)

        # סכום - mobile: type עוקף את בעיית ACTION_SET_PROGRESS ב-WebView
        self.page.amount_field.click()
        self.driver.execute_script('mobile: type', {'text': str(amount)})

        # תאריך - פתיחת DatePicker
        self.page.date_picker.click()
        time.sleep(1)
        if day:
            # בחירת יום ספציפי
            wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, f"//*[@text='{day}']")
            )).click()
        # אישור עם "הגדר"
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("הגדר")'
        ).click()

        # קטגוריה
        if category:
            self.page.category_dropdown.click()
            time.sleep(0.5)
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{category}")'
            ).click()

        # לחיצה על כפתור הוספה
        self.page.add_expense_button.click()

    def _wait_for_row(self, text: str):
        """ממתין לשורה המכילה את הטקסט ומחזיר אותה."""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
            )
        )

    # ──────────────────────────────────────────────
    # TC-001: בדיקת אלמנטי UI
    # ──────────────────────────────────────────────
    def test_tc001_verify_ui_elements(self):
        """TC-001: בדיקה שכל השדות במסך הראשי נטענים ומוצגים"""
        assert self.page.expense_name_field.is_displayed(), "שדה שם הוצאה לא מוצג"
        assert self.page.amount_field.is_displayed(), "שדה סכום לא מוצג"
        assert self.page.date_picker.is_displayed(), "שדה בחירת תאריך לא מוצג"
        assert self.page.category_dropdown.is_displayed(), "תפריט קטגוריות לא מוצג"
        assert self.page.add_expense_button.is_displayed(), "כפתור הוספה לא מוצג"

    # ──────────────────────────────────────────────
    # TC-002: DDT - הוספת הוצאות מקובץ JSON
    # ──────────────────────────────────────────────
    @pytest.mark.parametrize("expense", load_test_data(DATA_FILE_PATH))
    def test_tc002_add_multiple_expenses_ddt(self, expense):
        """TC-002: הוספת מספר הוצאות מקובץ JSON - Data Driven Testing"""
        self._add_expense(
            expense["name"],
            expense["amount"],
            category=expense.get("category")
        )

    # ──────────────────────────────────────────────
    # TC-003: הוספת הוצאה בסיסית + אימות ברשימה
    # ──────────────────────────────────────────────
    def test_tc003_add_expense_and_verify(self):
        """TC-003: הוספת הוצאה בסיסית ווידוא שמופיעה ברשימה"""
        self._add_expense("fruit", "100", day="15", category="Food")
        assert self._wait_for_row("fruit").is_displayed()

    # ──────────────────────────────────────────────
    # TC-004: Full Flow - הוספה מלאה עם כל השדות
    # ──────────────────────────────────────────────
    def test_tc004_full_flow_add_expense(self):
        """TC-004: Full flow - הוספת כרטיס רכבת עם כל השדות ווידוא"""
        self._add_expense("train ticket", "50", day="20", category="Transportation")
        assert self._wait_for_row("train ticket").is_displayed()

    # ──────────────────────────────────────────────
    # TC-005: בדיקת הפרעת מקלדת
    # ──────────────────────────────────────────────
    def test_tc005_keyboard_interference_check(self):
        """TC-005: בדיקה שהמקלדת לא מפריעה למילוי שדות"""
        self._add_expense("book", "30", day="25", category="Education")
        assert self._wait_for_row("book").is_displayed()

    # ──────────────────────────────────────────────
    # TC-006: עקביות נתונים לאחר restart
    # ──────────────────────────────────────────────
    def test_tc006_data_persistence_after_restart(self):
        """TC-006: עקביות נתונים לאחר הפעלה מחדש של האפליקציה"""
        self._add_expense("hotel", "200", day="10", category="Accommodation")
        assert self._wait_for_row("hotel").is_displayed()

        # שליחת האפליקציה לרקע ושובה לפוקוס (מדמה restart קל)
        self.driver.background_app(3)
        time.sleep(2)

        assert self._wait_for_row("hotel").is_displayed()