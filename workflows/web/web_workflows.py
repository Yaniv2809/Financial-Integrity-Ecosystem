import allure
from extensions.ui_actions import UIActions
from page_objects.web.expense_tracker_page import ExpenseTrackerPage

class WebWorkflows:

    @staticmethod
    @allure.step("Create a new expense in Web workflow")
    def create_expense(page, description, amount, category="Food", date="2023-10-15"):
        """
        מזין תיאור, סכום, קטגוריה ותאריך, ולוחץ על 'הוסף'.
        """
        UIActions.fill_text(page, ExpenseTrackerPage.txt_description, description)
        UIActions.fill_text(page, ExpenseTrackerPage.txt_amount, str(amount))

        UIActions.select_option(page, ExpenseTrackerPage.category_dropdown, category)
        UIActions.fill_text(page, ExpenseTrackerPage.add_date, date)
        
        UIActions.click(page, ExpenseTrackerPage.btn_add)