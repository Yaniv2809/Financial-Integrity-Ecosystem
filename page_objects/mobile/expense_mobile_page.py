"""
Page Object for the Atid Expense Tracker mobile app.
Contains only locator definitions — no actions, no find_element calls, no business logic.
"""


class MobileExpensePage:
    """Pure locator container for the Expense Tracker mobile app (WebView hybrid)."""

    # ── Input Fields (UiAutomator resourceId selectors) ──────────────
    EXPENSE_NAME_FIELD = 'new UiSelector().resourceId("expense-name")'
    AMOUNT_FIELD = 'new UiSelector().resourceId("expense-amount")'
    DATE_PICKER = 'new UiSelector().resourceId("expense-date")'
    CATEGORY_DROPDOWN = 'new UiSelector().resourceId("expense-category")'

    # ── Buttons ──────────────────────────────────────────────────────
    ADD_EXPENSE_BUTTON = 'new UiSelector().resourceId("add-expense")'
    DATE_CONFIRM_BUTTON = 'new UiSelector().text("\u05d4\u05d2\u05d3\u05e8")'  # Hebrew "Set" button

    # ── Dynamic Locators ─────────────────────────────────────────────

    @staticmethod
    def expense_by_text(text: str) -> str:
        """Dynamic locator for an expense item containing specific text."""
        return f'new UiSelector().textContains("{text}")'

    @staticmethod
    def category_option(category_name: str) -> str:
        """Dynamic locator for a category dropdown option."""
        return f'new UiSelector().text("{category_name}")'

    @staticmethod
    def delete_button_for(expense_name: str) -> str:
        """Dynamic XPath locator for the delete button of a specific expense."""
        return f"//*[contains(@text, '{expense_name}')]/..//*[@text='Delete']"
