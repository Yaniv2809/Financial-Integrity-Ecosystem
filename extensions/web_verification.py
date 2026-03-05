from playwright.sync_api import Locator, expect
from smart_assertions import soft_assert, verify_expectations
import allure

class WebVerify:
  
    @staticmethod    
    @allure.step("Verify that the element has text")
    def text(element: Locator, expected_text: str):
        """
        Verifies that the text of the element matches the expected text.
        """
        expect(element).to_have_text(expected_text)

    @staticmethod
    @allure.step("Verify String")
    def strings_are_equal(actual:str,expected:str,message=None):
        assert actual == expected,message

    @staticmethod
    @allure.step("Verify that the element is visible")
    def visible(element: Locator):
        """
        Verifies that the element is visible.
        """
        expect(element).to_be_visible()
    
    @staticmethod
    @allure.step("Verify that the element is not visible")
    def not_visible(element: Locator):
        expect(element).not_to_be_visible()
    
    @staticmethod
    @allure.step("Verifies that the number of elements matching the locator is equal to the expected count")
    def count(element: Locator, count: int):
        expect(element).to_have_count(count)

    @staticmethod
    @allure.step("Verify no new rows were added (expected: {expected_count})")
    def verify_no_row_added(element: Locator, expected_count: int, alert_text: str = None):
        """
        Verifies that no new row was added to the list.
        Prints actual vs expected count and the expected alert message.
        """
        actual_count = element.count()
        print(f"\n[VERIFY] Rows actual: {actual_count} | Rows expected: {expected_count}")
        if alert_text:
            print(f"[VERIFY] Expected alert was: '{alert_text}'")
        assert actual_count == expected_count, (
            f"BUG: Row was added despite invalid input! "
            f"Expected {expected_count} rows, got {actual_count}"
        )

    @staticmethod
    @allure.step("Verify that the element contains the expected text")
    def contain_text(element: Locator, expected_text: str):
        expect(element).to_contain_text(expected_text)
    
    @staticmethod
    @allure.step("Verify that the element has the expected value")
    def value(element: Locator, expected_value: str):
        """
        Verifies that the value of the element matches the expected value.
        """
        expect(element).to_have_value(expected_value)


    # Soft Assertions    
    @staticmethod
    @allure.step("Soft assertion to check if the element has the expected text")
    def soft_text(element: Locator, expected_text: str, message: str):
        """
        Soft assertion to check if the element has the expected text.
        Test execution will continue even if this assertion fails.
        """
        actual_text = element.inner_text()
        soft_assert(actual_text == expected_text, message)

    @staticmethod
    @allure.step("Soft assertion to check if the element is visible")
    def soft_is_visible(element: Locator, message: str):
        """
        Soft assertion to check if the element is visible.
        Test execution will continue even if this assertion fails.
        """
        soft_assert(element.is_visible(), message)

    @staticmethod
    @allure.step("Raises all collected assertion errors at once")
    def soft_all():
        """Raises all collected assertion errors at once."""
        verify_expectations()


    @staticmethod
    @allure.step("Verify that the element count is exactly {expected_count}")
    def verify_element_count(element, expected_count: int):
        """
       verifies that the number of elements matching the locator is equal to the expected count.
        """
        expect(element).to_have_count(expected_count, timeout=5000)

    @staticmethod
    @allure.step("Verify element does not overflow its parent container")
    def verify_no_container_overflow(element):
        """
       checks if the element's text overflows its parent container (e.g., a card) and asserts that it does not.
        This is useful for catching UI bugs where long text might break the layout.
        """
        is_overflowing = element.evaluate(
            "(el) => {"
            "  const parent = el.parentElement;"
            "  /* checks if the element's text overflows its parent container */"
            "  return el.getBoundingClientRect().right > parent.getBoundingClientRect().right || "
            "         el.scrollWidth > el.clientWidth;"
            "}"
        )
        assert not is_overflowing, "UI Bug: The text overflows its parent container (the card)!"

    @staticmethod
    @allure.step("Soft Verify condition is True")
    def soft_is_true(condition: bool, message: str = "Condition expected to be True but was False"):
        soft_assert(condition is True, message)

    @staticmethod
    @allure.step("Soft Verify Strings are equal")
    def soft_strings_are_equal(actual: str, expected: str, message=None):
        soft_assert(actual == expected, message)