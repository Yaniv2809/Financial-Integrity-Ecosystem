import time
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from page_objects.mobile.atid_expense_appium_page import AtidExpenseAppiumPage
from selenium.webdriver.common.by import By


class MobileActions(AtidExpenseAppiumPage):

    def __init__(self, driver):
        self.driver = driver


    def add_full_expense(self, name, amount,category=None):
        """function that adds an expense with all details (name, amount, date, category)"""
        # שם הוצאה
        self.expense_name_field.click()
        self.expense_name_field.clear()
        self.expense_name_field.send_keys(name)

        # סכום
        self.amount_field.click()
        self.driver.execute_script('mobile: type', {'text': str(amount)})

        # תאריך
        # תאריך - לחיצה על DatePicker ואישור עם "הגדר"
        self.date_picker.click()
        import time
        time.sleep(1)
        ok_btn = self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("הגדר")')
        ok_btn.click()
       

        # קטגוריה
        if category:
            self.category_dropdown.click()
            option = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{category}")')
            option.click()

        # לחיצה על כפתור הוספה
        self.add_expense_button.click()

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

    


    @staticmethod
    def is_displayed(name, driver):
        locator = (By.XPATH, f"//*[contains(@text, '{name}')]")
        assert driver.find_element(*locator).is_displayed(), f"Element with text {name} was not found!"
   #is_displayed(name, driver) → בודקת טקסט בלבד

    @staticmethod
    def visible(driver, locator):
        assert driver.find_element(*locator).is_displayed(), \
            f"Element {locator} was not found!"   
    #visible(driver, locator) → בודקת locator ספציפי
    
    @staticmethod
    @allure.step("Verify expense added to table")
    def verify_expense_added(driver, name: str, amount: str):

        name_locator = (By.XPATH, f"//*[@text='{name}']")
        amount_locator = (By.XPATH, f"//*[@text='{amount}']")

        assert driver.find_element(*name_locator).is_displayed(), \
            f"Expense name '{name}' not found!"

        assert driver.find_element(*amount_locator).is_displayed(), \
            f"Expense amount '{amount}' not found!"     


    @staticmethod
    @allure.step("Verify expense was deleted")
    def verify_deleted(driver, name: str):
        # שימוש ב-find_elements (ברבים) מחזיר רשימה
        locator = (By.XPATH, f"//*[contains(@text, '{name}')]")
        elements = driver.find_elements(*locator)
        
        # אם האורך הוא 0, סימן שזה לא נמצא = הצלחה!
        assert len(elements) == 0, f"Failure: The expense '{name}' still exists in the list."    


