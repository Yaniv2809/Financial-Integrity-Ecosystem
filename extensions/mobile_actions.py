"""
Mobile Actions — static action methods for Appium automation.
Mirrors UIActions from the web layer. Uses WebDriverWait (no time.sleep).
"""
import os
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from utils.logger import Logger

log = Logger()
DEFAULT_TIMEOUT = 10


class MobileActions:
    """
    Static action methods for mobile automation.
    All methods take driver as first parameter and use explicit waits.
    """

    # ── Internal Helper ──────────────────────────────────────────────

    @staticmethod
    def _find(driver, locator: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Wait for and return a single element using UiAutomator selector.
        Internal helper — not decorated with allure.step.
        """
        return WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator)
        )

    # ── Alert Handling ────────────────────────────────────────────────

    @staticmethod
    @allure.step("Mobile Action: Dismiss alert/dialog if present")
    def dismiss_alert_if_present(driver):
        """Dismiss any alert or dialog that may be blocking the screen."""
        # Temporarily disable implicit wait so failed find_element calls return instantly
        driver.implicitly_wait(0)
        try:
            # Strategy 1: Native Android alert
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                log.info(f"Mobile Action: Native alert found: '{alert_text}' — accepting")
                alert.accept()
                return
            except Exception:
                pass

            # Strategy 2: WebView/Android dialog buttons
            confirm_texts = ["OK", "אישור", "Confirm", "Accept", "Yes", "Got it", "ALLOW", "Allow"]
            for text in confirm_texts:
                try:
                    btn = driver.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().text("{text}").clickable(true)'
                    )
                    if btn.is_displayed():
                        log.info(f"Mobile Action: Dialog button '{text}' found — clicking")
                        btn.click()
                        return
                except Exception:
                    continue

            # Strategy 3: Android dialog positive button by ID
            try:
                btn = driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().resourceId("android:id/button1")'
                )
                if btn.is_displayed():
                    log.info("Mobile Action: Android dialog button1 found — clicking")
                    btn.click()
                    return
            except Exception:
                pass
        finally:
            # Restore implicit wait
            driver.implicitly_wait(DEFAULT_TIMEOUT)

    # ── App Lifecycle ─────────────────────────────────────────────────

    @staticmethod
    @allure.step("Mobile Action: Ensure app is in foreground")
    def ensure_app_active(driver, package: str = "com.atidcollege.atidexpensetracker"):
        """Re-activate the app if it was killed or sent to background."""
        try:
            state = driver.query_app_state(package)
            # State 4 = running in foreground, 3 = running in background
            if state < 3:
                log.info(f"Mobile Action: App state={state}, re-activating...")
                driver.activate_app(package)
                import time
                time.sleep(2)  # Wait for app to fully load
            elif state == 3:
                log.info("Mobile Action: App in background, bringing to foreground")
                driver.activate_app(package)
                import time
                time.sleep(1)
        except Exception:
            log.info("Mobile Action: Could not check app state, attempting activate")
            driver.activate_app(package)
            import time
            time.sleep(2)

    # ── Core Actions ─────────────────────────────────────────────────

    @staticmethod
    @allure.step("Mobile Action: Click element — {locator}")
    def click(driver, locator: str, timeout: int = DEFAULT_TIMEOUT):
        """Find element by UiAutomator selector and click it."""
        log.info(f"Mobile Action: Clicking element '{locator}'")
        element = MobileActions._find(driver, locator, timeout)
        element.click()

    @staticmethod
    @allure.step("Mobile Action: Fill text '{text}' into element — {locator}")
    def fill_text(driver, locator: str, text: str, timeout: int = DEFAULT_TIMEOUT):
        """Clear field and type text using UiAutomator selector."""
        log.info(f"Mobile Action: Filling '{text}' into element '{locator}'")
        element = MobileActions._find(driver, locator, timeout)
        element.click()
        element.clear()
        element.send_keys(text)

    @staticmethod
    @allure.step("Mobile Action: Type text '{text}' via mobile:type script")
    def type_via_script(driver, text: str):
        """Use Appium mobile:type for fields that don't accept send_keys cleanly."""
        log.info(f"Mobile Action: Typing '{text}' via mobile:type script")
        driver.execute_script('mobile: type', {'text': str(text)})

    @staticmethod
    @allure.step("Mobile Action: Get text from element — {locator}")
    def get_text(driver, locator: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        """Return text content of element."""
        element = MobileActions._find(driver, locator, timeout)
        text = element.text
        log.info(f"Mobile Action: Got text '{text}' from element '{locator}'")
        return text

    @staticmethod
    @allure.step("Mobile Action: Clear text in element — {locator}")
    def clear(driver, locator: str, timeout: int = DEFAULT_TIMEOUT):
        """Clear text from input field."""
        log.info(f"Mobile Action: Clearing element '{locator}'")
        element = MobileActions._find(driver, locator, timeout)
        element.clear()

    # ── Device Actions ───────────────────────────────────────────────

    @staticmethod
    @allure.step("Mobile Action: Press Android back button")
    def press_back(driver):
        """Press the hardware back button."""
        log.info("Mobile Action: Pressing back button")
        driver.press_keycode(4)

    @staticmethod
    @allure.step("Mobile Action: Send app to background for {seconds} seconds")
    def background_app(driver, seconds: int = 3):
        """Put app in background and bring back after N seconds."""
        log.info(f"Mobile Action: Sending app to background for {seconds}s")
        driver.background_app(seconds)

    @staticmethod
    @allure.step("Mobile Action: Set device orientation to {orientation}")
    def set_orientation(driver, orientation: str):
        """Set device orientation: PORTRAIT or LANDSCAPE."""
        log.info(f"Mobile Action: Setting orientation to {orientation}")
        driver.orientation = orientation

    @staticmethod
    @allure.step("Mobile Action: Hide keyboard if visible")
    def hide_keyboard(driver):
        """Hide the on-screen keyboard if it is displayed."""
        try:
            if driver.is_keyboard_shown():
                driver.hide_keyboard()
                log.info("Mobile Action: Keyboard hidden")
        except Exception:
            log.info("Mobile Action: Keyboard was not visible or could not be hidden")

    @staticmethod
    @allure.step("Mobile Action: Take screenshot — {name}")
    def screenshot(driver, name: str):
        """Save screenshot to reports/screenshots directory."""
        screenshot_dir = os.path.join("reports", "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f"{name}.png")
        driver.save_screenshot(path)
        log.info(f"Mobile Action: Screenshot saved to {path}")
        return path

    # ── Scroll Actions ─────────────────────────────────────────────────

    @staticmethod
    @allure.step("Mobile Action: Scroll to top of the screen")
    def scroll_to_top(driver):
        """Scroll to the top using swipe gestures. Avoids UiScrollable which can hang on WebViews."""
        log.info("Mobile Action: Scrolling to top of the screen")
        try:
            size = driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] // 4
            end_y = size['height'] * 3 // 4
            # Perform 3 quick swipe-down gestures (pulls content up = scroll to top)
            for _ in range(3):
                driver.swipe(start_x, start_y, start_x, end_y, 500)
                import time
                time.sleep(0.3)
        except Exception:
            log.info("Mobile Action: Could not scroll to top — may already be at top")

    @staticmethod
    @allure.step("Mobile Action: Scroll element into view — {locator}")
    def scroll_to_element(driver, locator: str):
        """Scroll until element with UiAutomator selector is visible."""
        log.info(f"Mobile Action: Scrolling to element '{locator}'")
        try:
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({locator})'
            )
        except Exception:
            log.info(f"Mobile Action: Scroll to element failed — element may already be visible")

    # ── XPath-based Actions (for delete buttons, dynamic elements) ───

    @staticmethod
    @allure.step("Mobile Action: Click element by XPath — {xpath}")
    def click_xpath(driver, xpath: str, timeout: int = DEFAULT_TIMEOUT):
        """Find element by XPath and click it."""
        log.info(f"Mobile Action: Clicking XPath element '{xpath}'")
        element = WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(AppiumBy.XPATH, xpath)
        )
        element.click()

    @staticmethod
    @allure.step("Mobile Action: Click delete button for expense — {expense_name}")
    def click_delete_for_expense(driver, expense_name: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Find and click the delete button for a specific expense.
        Tries multiple XPath strategies for compatibility with different DOM structures.
        """
        log.info(f"Mobile Action: Deleting expense '{expense_name}'")
        xpaths = [
            # Strategy 1: Exact "Delete" text button in same parent container
            f"//*[contains(@text, '{expense_name}')]/..//*[@text='Delete']",
            # Strategy 2: Delete button as following-sibling with exact text
            f"//*[contains(@text, '{expense_name}')]/following-sibling::*[@text='Delete']",
            # Strategy 3: Any Button element in same parent
            f"//*[contains(@text, '{expense_name}')]/..//android.widget.Button[@text='Delete']",
            # Strategy 4: Fallback — contains text (case insensitive)
            f"//*[contains(@text, '{expense_name}')]/..//*[contains(@text, 'Delete') or contains(@text, 'delete')]",
            # Strategy 5: Resource-id based delete button in same parent
            f"//*[contains(@text, '{expense_name}')]/..//*[contains(@resource-id, 'delete')]",
        ]
        for xpath in xpaths:
            try:
                element = WebDriverWait(driver, 3).until(
                    lambda d, x=xpath: d.find_element(AppiumBy.XPATH, x)
                )
                element.click()
                log.info(f"Mobile Action: Delete clicked using XPath: {xpath}")
                return
            except Exception:
                continue
        # If all XPaths fail, raise with helpful message
        raise Exception(
            f"Could not find delete button for expense '{expense_name}'. "
            f"Tried {len(xpaths)} XPath strategies. "
            f"Please inspect the app DOM with driver.page_source to find the correct locator."
        )
