"""
Mobile Workflows — high-level business flow orchestration.
Mirrors WebWorkflows from the web layer. All static methods.
"""
import allure
from extensions.mobile_actions import MobileActions
from page_objects.mobile.expense_mobile_page import MobileExpensePage


class MobileWorkflows:
    """
    Workflow orchestration for mobile expense operations.
    All methods are static, taking driver as first parameter.
    Composes atomic actions from MobileActions.
    """

    @staticmethod
    @allure.step("Workflow: Create expense — name={name}, amount={amount}, category={category}")
    def create_expense(driver, name: str, amount: str, category: str = None):
        """
        Full expense creation flow:
        0. Scroll to top to ensure input fields are visible
        1. Fill expense name
        2. Fill amount (via mobile:type script for WebView compatibility)
        3. Open date picker and confirm default date
        4. Optionally select category from dropdown
        5. Click Add Expense button
        """
        # 0. Ensure app is active, dismiss alerts, scroll to top
        MobileActions.ensure_app_active(driver)
        MobileActions.dismiss_alert_if_present(driver)
        MobileActions.scroll_to_top(driver)

        # 1. Fill expense name
        MobileActions.fill_text(driver, MobileExpensePage.EXPENSE_NAME_FIELD, name)

        # 2. Fill amount — use type_via_script for WebView ACTION_SET_PROGRESS bypass
        MobileActions.click(driver, MobileExpensePage.AMOUNT_FIELD)
        MobileActions.type_via_script(driver, str(amount))

        # 3. Open date picker and confirm with default date
        MobileActions.click(driver, MobileExpensePage.DATE_PICKER)
        MobileActions.click(driver, MobileExpensePage.DATE_CONFIRM_BUTTON)

        # 4. Select category if provided
        if category:
            MobileActions.click(driver, MobileExpensePage.CATEGORY_DROPDOWN)
            MobileActions.click(driver, MobileExpensePage.category_option(category))

        # 5. Submit and dismiss any alert that appears
        MobileActions.click(driver, MobileExpensePage.ADD_EXPENSE_BUTTON)
        MobileActions.dismiss_alert_if_present(driver)

    @staticmethod
    @allure.step("Workflow: Create minimal expense — name={name}, amount={amount}")
    def create_expense_minimal(driver, name: str, amount: str):
        """
        Minimal expense creation: name + amount + confirm date. No category.
        """
        MobileActions.ensure_app_active(driver)
        MobileActions.dismiss_alert_if_present(driver)
        MobileActions.scroll_to_top(driver)
        MobileActions.fill_text(driver, MobileExpensePage.EXPENSE_NAME_FIELD, name)
        MobileActions.click(driver, MobileExpensePage.AMOUNT_FIELD)
        MobileActions.type_via_script(driver, str(amount))
        MobileActions.click(driver, MobileExpensePage.DATE_PICKER)
        MobileActions.click(driver, MobileExpensePage.DATE_CONFIRM_BUTTON)
        MobileActions.click(driver, MobileExpensePage.ADD_EXPENSE_BUTTON)

    @staticmethod
    @allure.step("Workflow: Delete expense containing text — {text}")
    def delete_expense(driver, text: str):
        """
        Find an expense by its text content and click its delete button.
        Uses multi-strategy XPath approach for DOM compatibility.
        After deletion, dismisses any confirmation alert and scrolls to top.
        """
        MobileActions.ensure_app_active(driver)
        MobileActions.click_delete_for_expense(driver, text)
        MobileActions.dismiss_alert_if_present(driver)
        # Scroll to top to reset view after deletion
        MobileActions.scroll_to_top(driver)
