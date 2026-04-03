import allure
from playwright.sync_api import Page
from extensions.ui_actions import UIActions
from page_objects.web.expense_tracker_page import ExpenseTrackerPage

class WebWorkflows:

    @staticmethod
    @allure.step("Create a new expense in Web workflow")
    def create_expense(page, expense_name, amount=100, category="Food", date="2023-10-15"):
        UIActions.clear_field(page, ExpenseTrackerPage.expense_name)
        UIActions.clear_field(page, ExpenseTrackerPage.txt_amount)
        UIActions.fill_text(page, ExpenseTrackerPage.expense_name, expense_name)
        UIActions.fill_text(page, ExpenseTrackerPage.txt_amount, str(amount))
        UIActions.select_option(page, ExpenseTrackerPage.category_dropdown, category)
        UIActions.fill_text(page, ExpenseTrackerPage.add_date, date)
        UIActions.click(page, ExpenseTrackerPage.btn_add)


    @staticmethod
    @allure.step("Fill expense form and catch expected alert")
    def validate_expense_and_alert(page, expense_name, amount, category="Food", date="2023-10-15"):
        # 1. יצרנו מילון ריק לאיסוף הנתונים
        alert_received = {"appeared": False, "text": ""}

        # 2. פונקציית הקולבק
        def on_dialog(dialog):
            alert_received["appeared"] = True
            alert_received["text"] = dialog.message
            dialog.accept()
        # 3. מחברים את המאזין
        page.once("dialog", on_dialog)
        # 4. ממלאים את הרשומה
        UIActions.fill_text(page, ExpenseTrackerPage.expense_name, expense_name)
        amount_locator = page.locator(ExpenseTrackerPage.txt_amount)
        amount_locator.click()
        amount_locator.press_sequentially(str(amount), delay=50)
        UIActions.fill_text(page, ExpenseTrackerPage.add_date, date)
        UIActions.select_option(page, ExpenseTrackerPage.category_dropdown, category)       
        # 5. לחיצה על כפתור ההוספה (הטריגר של האלרט)
        UIActions.click(page, ExpenseTrackerPage.btn_add)
        # מחכים חצי שנייה כדי לתת לאלרט הזדמנות לקפוץ
        page.wait_for_timeout(500)
        # 6. התיקון הקריטי: מסירים את המאזין כדי שלא "ילכלך" טסטים הבאים!
        page.remove_listener("dialog", on_dialog)
        return alert_received
    


    @staticmethod
    @allure.step("Validate Boundary Expense - status: {expected_status}")
    def validate_boundary_expense(page, expense_name, amount, date, category, expected_status):
        """
        מבצע ניסיון הוספת הוצאה ומחזיר את התוצאות לאימות.
        מטפל ב-Alert אם צפוי כישלון, ובהכפלת טקסט ארוך.
        """
        # הכפלת טקסט ארוך לבדיקת boundary
        if len(expense_name) > 20 and set(expense_name) == {"A"}:
            expense_name = "A" * 200

        # ספירת שורות לפני
        initial_count = page.locator(ExpenseTrackerPage.expense_name_items).count()

        # טיפול ב-Alert אם צפוי כישלון
        alert_received = {"appeared": False, "text": ""}
        if expected_status == "failure":
            def on_dialog(dialog):
                alert_received["appeared"] = True
                alert_received["text"] = dialog.message
                dialog.accept()
            page.once("dialog", on_dialog)

        # יצירת ההוצאה
        UIActions.fill_text(page, ExpenseTrackerPage.expense_name, expense_name)
        UIActions.fill_text(page, ExpenseTrackerPage.txt_amount, str(amount))
        UIActions.fill_text(page, ExpenseTrackerPage.add_date, date)
        UIActions.select_option(page, ExpenseTrackerPage.category_dropdown, category)
        UIActions.click(page, ExpenseTrackerPage.btn_add)
        page.wait_for_timeout(500)

        return {
            "expense_name": expense_name,
            "initial_count": initial_count,
            "alert": alert_received
        }
    
    @staticmethod
    @allure.step("Simulate UI failure to trigger AI error analysis")
    def simulate_ui_failure_for_ai(page: Page):
        UIActions.click(
            page=page, 
            selector=ExpenseTrackerPage.non_existent_ai_button, 
            timeout=2000
        )

    @staticmethod
    @allure.step("Delete expense by name: {expense_name}")
    def delete_expense_by_name(page: Page, expense_name: str):
        row = page.locator(ExpenseTrackerPage.expense_list).locator("li").filter(has_text=expense_name)
        row.locator("button").click(timeout=3000)