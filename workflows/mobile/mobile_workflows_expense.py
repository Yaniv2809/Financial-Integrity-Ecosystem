from page_objects.mobile.expense_mobile_page import MobileExpensePage


class MobileWorkflows:

    def __init__(self, driver):
        self.driver   = driver
        self.expense  = MobileExpensePage(driver)

    # ── Expense ───────────────────────────────────────────────────────────
    def add_expense_flow(self, name, amount, category=None):
        self.expense.add_full_expense(name, amount, category=category)

