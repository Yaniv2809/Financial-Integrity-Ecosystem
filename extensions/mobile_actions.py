import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


class MobileActions:

    def __init__(self, driver):
        self.driver = driver

    # ── Find ────────────────────────────────────────────────────────────
    def find_by_text(self, text):
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{text}")')

    def find_by_id(self, resource_id):
        return self.driver.find_element(AppiumBy.ID, resource_id)

    def find_by_xpath(self, xpath):
        return self.driver.find_element(AppiumBy.XPATH, xpath)

    def get_all_inputs(self):
        return self.driver.find_elements(AppiumBy.XPATH, '//android.widget.EditText')

    # ── Interact ─────────────────────────────────────────────────────────
    def tap_text(self, *texts):
        for text in texts:
            try:
                self.find_by_text(text).click()
                time.sleep(0.5)
                return True
            except NoSuchElementException:
                continue
        return False

    def tap_button_by_index(self, index=0):
        buttons = self.driver.find_elements(AppiumBy.XPATH, '//android.widget.Button')
        if index < len(buttons):
            buttons[index].click()
            return True
        return False

    def fill_input(self, index, value):
        inputs = self.get_all_inputs()
        if index < len(inputs):
            inputs[index].clear()
            inputs[index].send_keys(value)

    def press_back(self):
        self.driver.press_keycode(4)
        time.sleep(0.5)

    def background_app(self, seconds=3):
        self.driver.background_app(seconds)

    def set_orientation(self, orientation):
        self.driver.orientation = orientation

    def set_network(self, mode):
        """0=offline, 6=wifi+data"""
        self.driver.set_network_connection(mode)

    # ── State ────────────────────────────────────────────────────────────
    def has_text(self, *texts):
        for text in texts:
            try:
                self.find_by_text(text)
                return True
            except NoSuchElementException:
                continue
        return False

    def is_active(self):
        return self.driver.current_activity is not None

    def screenshot(self, name):
        import os
        os.makedirs("logs/screenshots", exist_ok=True)
        self.driver.save_screenshot(f"logs/screenshots/{name}.png")