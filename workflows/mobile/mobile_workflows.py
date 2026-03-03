from page_objects.mobile.expense_mobile_page import ExpensePage


class MobileWorkflows:

    def __init__(self, driver):
        self.driver   = driver
        self.expense  = ExpensePage(driver)

    # ── Expense ───────────────────────────────────────────────────────────
    def add_expense_flow(self, amount, description):
        self.expense.add_expense(amount, description)

