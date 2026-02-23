import allure
import pytest
from workflows.web_workflows import WebWorkflows
from extensions.ui_actions import UIActions
from config.config import ConfigManager  # שים לב שאני משתמש בשם הקובץ שיש לך בגיטהאב
from extensions.verifications import Verifications

class TestWeb:
    """
    מחלקת טסטים עבור ממשק המשתמש (Web).
    מעבירים את המשתנה 'page' (מיוצר אוטומטית ע"י Playwright) לתוך הטסט.
    """

    @allure.title("Create a new expense via Web UI")
    @allure.description("This test opens the browser, navigates to the app, and adds an expense")
    def test_create_expense_web(self, page):
        # 1. ניווט לאתר ה-Web (מושך את הכתובת מ-config.json)
        url = ConfigManager.get_env_data()['web_url']
        UIActions.navigate(page, url)
        
        # 2. ביצוע הפעולה העסקית (קריאה לוורקפלו המעודכן שלנו)
        WebWorkflows.create_expense(
            page=page, 
            description="Business Lunch Web", 
            amount=150, 
            category="Food", 
            date="2024-05-20"
        )
        
        # 3. אימות (Verification) - מוודאים שהטקסט שהכנסנו באמת מופיע בתוך טבלת ההוצאות!
        # אנו קוראים את כל הטקסט של הטבלה ומוודאים שהתיאור שלנו נמצא שם
        table_text = UIActions.get_text(page, "tbody")
        Verifications.verify_contains(table_text, "Business Lunch Web", "The new expense was not found in the table!")