"""
Mobile Verifications — static assertion methods for mobile testing.
Mirrors WebVerify from the web layer. All methods use explicit waits.
"""
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from utils.logger import Logger

log = Logger()
DEFAULT_TIMEOUT = 10


class MobileVerify:
    """
    Static verification methods for mobile testing.
    All methods take driver as first parameter.
    """

    @staticmethod
    @allure.step("Verify element is displayed: {locator}")
    def element_displayed(driver, locator: str, timeout: int = DEFAULT_TIMEOUT):
        """Assert that an element matching the UiAutomator selector is displayed."""
        element = WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
        )
        assert element.is_displayed(), f"Element '{locator}' exists but is not displayed"
        log.info(f"Verify: Element '{locator}' is displayed")

    @staticmethod
    @allure.step("Verify element is NOT displayed: {locator}")
    def element_not_displayed(driver, locator: str, timeout: int = 3):
        """Assert that no element matching the selector is visible (short timeout)."""
        driver.implicitly_wait(1)
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
            )
            assert False, f"Element '{locator}' should NOT be displayed but was found"
        except TimeoutException:
            log.info(f"Verify: Element '{locator}' is correctly not displayed")
        finally:
            driver.implicitly_wait(10)

    @staticmethod
    @allure.step("Verify text equals '{expected}' in element: {locator}")
    def text_equals(driver, locator: str, expected: str, timeout: int = DEFAULT_TIMEOUT):
        """Assert element text matches expected string exactly."""
        element = WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
        )
        actual = element.text
        assert actual == expected, (
            f"Text mismatch in '{locator}': expected '{expected}', got '{actual}'"
        )
        log.info(f"Verify: Text in '{locator}' equals '{expected}'")

    @staticmethod
    @allure.step("Verify element contains text '{expected}': {locator}")
    def text_contains(driver, locator: str, expected: str, timeout: int = DEFAULT_TIMEOUT):
        """Assert element text contains the expected substring."""
        element = WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
        )
        actual = element.text
        assert expected in actual, (
            f"Text '{expected}' not found in element '{locator}'. Actual text: '{actual}'"
        )
        log.info(f"Verify: Element '{locator}' contains text '{expected}'")

    @staticmethod
    @allure.step("Verify text '{text}' exists on screen")
    def text_on_screen(driver, text: str, timeout: int = DEFAULT_TIMEOUT):
        """Assert that text exists anywhere on the current screen (scrolls if needed)."""
        locator = f'new UiSelector().textContains("{text}")'
        try:
            element = WebDriverWait(driver, timeout).until(
                lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
            )
            assert element.is_displayed(), f"Text '{text}' found but not displayed"
            log.info(f"Verify: Text '{text}' found on screen")
        except TimeoutException:
            # Strategy 2: Try scrolling down to find it
            try:
                scroll_locator = (
                    f'new UiScrollable(new UiSelector().scrollable(true))'
                    f'.scrollIntoView(new UiSelector().textContains("{text}"))'
                )
                element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_locator)
                assert element.is_displayed(), f"Text '{text}' found after scroll but not displayed"
                log.info(f"Verify: Text '{text}' found on screen after scrolling")
            except Exception:
                # Strategy 3: Fallback — check raw page_source XML for WebView content
                source = driver.page_source
                if text in source:
                    log.info(f"Verify: Text '{text}' found in page_source (WebView element)")
                else:
                    assert False, f"Text '{text}' was NOT found anywhere on the screen (even after scrolling)"

    @staticmethod
    @allure.step("Verify text '{text}' is NOT on screen")
    def text_not_on_screen(driver, text: str, timeout: int = 3):
        """Assert that text does NOT appear anywhere on the screen."""
        locator = f'new UiSelector().textContains("{text}")'
        # Use short implicit wait for negative check
        driver.implicitly_wait(1)
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
            )
            assert False, f"Text '{text}' should NOT be on screen but was found"
        except TimeoutException:
            log.info(f"Verify: Text '{text}' is correctly not on screen")
        finally:
            driver.implicitly_wait(10)

    @staticmethod
    @allure.step("Verify element count equals {expected_count}")
    def element_count(driver, locator: str, expected_count: int, timeout: int = DEFAULT_TIMEOUT):
        """Assert the number of elements matching locator equals expected count."""
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, locator)) > 0
        )
        elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, locator)
        actual = len(elements)
        assert actual == expected_count, (
            f"Element count mismatch for '{locator}': expected {expected_count}, got {actual}"
        )
        log.info(f"Verify: Element count for '{locator}' is {expected_count}")

    @staticmethod
    @allure.step("Verify keyboard is not displayed")
    def keyboard_not_visible(driver):
        """Assert the on-screen keyboard is hidden."""
        is_shown = driver.is_keyboard_shown()
        assert not is_shown, "Keyboard should be hidden but is still displayed"
        log.info("Verify: Keyboard is not visible")
