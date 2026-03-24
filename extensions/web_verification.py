from playwright.sync_api import Page, expect
from smart_assertions import soft_assert, verify_expectations
import allure
import re

class WebVerify:
    
    @staticmethod    
    @allure.step("Verify that element '{selector}' has text '{expected_text}'")
    def text(page: Page, selector: str, expected_text: str):
        """
        Verifies that the text of the element matches the expected text.
        """
        expect(page.locator(selector)).to_have_text(expected_text)

    @staticmethod
    @allure.step("Verify String: '{actual}' == '{expected}'")
    def strings_are_equal(actual: str, expected: str, message: str = None):
        assert actual == expected, message

    @staticmethod
    @allure.step("Verify that element '{selector}' is visible")
    def visible(page: Page, selector: str):
        """
        Verifies that the element is visible.
        """
        expect(page.locator(selector)).to_be_visible()
    
    @staticmethod
    @allure.step("Verify that element '{selector}' is not visible")
    def not_visible(page: Page, selector: str):
        expect(page.locator(selector)).not_to_be_visible()
    
    @staticmethod
    @allure.step("Verify that the number of elements matching '{selector}' is equal to {expected_count}")
    def count(page: Page, selector: str, expected_count: int):
        expect(page.locator(selector)).to_have_count(expected_count)

    @staticmethod
    @allure.step("Verify no new rows were added to '{selector}' (expected: {expected_count})")
    def verify_no_row_added(page: Page, selector: str, expected_count: int, alert_text: str = None):
        """
        Verifies that no new row was added to the list.
        Prints actual vs expected count and the expected alert message.
        """
        actual_count = page.locator(selector).count()
        print(f"\n[VERIFY] Rows actual: {actual_count} | Rows expected: {expected_count}")
        if alert_text:
            print(f"[VERIFY] Expected alert was: '{alert_text}'")
        assert actual_count == expected_count, (
            f"BUG: Row was added despite invalid input! "
            f"Expected {expected_count} rows, got {actual_count}"
        )

    @staticmethod
    @allure.step("Verify that element '{selector}' contains the text '{expected_text}'")
    def contain_text(page: Page, selector: str, expected_text: str):
        expect(page.locator(selector)).to_contain_text(expected_text)
    
    @staticmethod
    @allure.step("Verify that element '{selector}' has the value '{expected_value}'")
    def value(page: Page, selector: str, expected_value: str):
        """
        Verifies that the value of the element matches the expected value.
        """
        expect(page.locator(selector)).to_have_value(expected_value)

    @staticmethod
    @allure.step("Verify that element '{selector}' contains text '{expected_text}' (ignore case)")
    def contain_text_ignore_case(page: Page, selector: str, expected_text: str):
        """
        Verifies that the element contains the expected text, ignoring case sensitivity.
        """
        expect(page.locator(selector)).to_have_text(re.compile(expected_text, re.IGNORECASE))

    @staticmethod
    @allure.step("Verify that the element '{selector}' count is exactly {expected_count}")
    def verify_element_count(page: Page, selector: str, expected_count: int):
        """
        Verifies that the number of elements matching the locator is equal to the expected count.
        """
        locator = page.locator(selector)
        expect(locator).to_have_count(expected_count, timeout=3000)

    @staticmethod
    @allure.step("Verify element '{selector}' does not overflow its parent container")
    def verify_no_container_overflow(page: Page, selector: str):
        """
        Checks if the element's text overflows its parent container (e.g., a card) and asserts that it does not.
        This is useful for catching UI bugs where long text might break the layout.
        """
        # שימוש ב-.first כדי להבטיח ש-evaluate ירוץ על אלמנט בודד ולא יקרוס אם יש כמה תוצאות
        locator = page.locator(selector).first
        is_overflowing = locator.evaluate(
            "(el) => {"
            "  const parent = el.parentElement;"
            "  /* checks if the element's text overflows its parent container */"
            "  return el.getBoundingClientRect().right > parent.getBoundingClientRect().right || "
            "         el.scrollWidth > el.clientWidth;"
            "}"
        )
        assert not is_overflowing, f"UI Bug: The text in '{selector}' overflows its parent container!"

    @staticmethod
    @allure.step("Soft Verify condition is True")
    def soft_is_true(condition: bool, message: str = "Condition expected to be True but was False"):
        soft_assert(condition is True, message)

    @staticmethod
    @allure.step("Soft Verify Strings are equal")
    def soft_strings_are_equal(actual: str, expected: str, message=None):
        soft_assert(actual == expected, message)

    # Soft Assertions    
    @staticmethod
    @allure.step("Soft assertion: Check if element '{selector}' has text '{expected_text}'")
    def soft_text(page: Page, selector: str, expected_text: str, message: str):
        """
        Soft assertion to check if the element has the expected text.
        Test execution will continue even if this assertion fails.
        """
        actual_text = page.locator(selector).inner_text()
        soft_assert(actual_text == expected_text, message)

    @staticmethod
    @allure.step("Soft assertion: Check if element '{selector}' is visible")
    def soft_is_visible(page: Page, selector: str, message: str):
        """
        Soft assertion to check if the element is visible.
        Test execution will continue even if this assertion fails.
        """
        is_vis = page.locator(selector).is_visible()
        soft_assert(is_vis, message)

    @staticmethod
    @allure.step("Raises all collected assertion errors at once")
    def soft_all():
        """Raises all collected assertion errors at once."""
        verify_expectations()