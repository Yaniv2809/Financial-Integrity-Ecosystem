from appium.webdriver.common.appiumby import AppiumBy

class MobileExpensePage:
    def __init__(self, driver):
        self.driver = driver

    @property
    def expense_name_field(self):
        return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("expense-name")')

    @property
    def amount_field(self):
        return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("expense-amount")')

    @property
    def date_picker(self):
        return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("expense-date")')

    @property
    def category_dropdown(self):
        return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("expense-category")')

    @property
    def add_expense_button(self):
        return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("add-expense")')

    
    def add_full_expense(self, name, amount,category=None):
        """פונקציה המבצעת את תהליך הוספת ההוצאה המלא"""
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
    # # ================= Actions =================
    # def add_full_expense(self, name, amount):
    #     """פונקציה המבצעת את תהליך הוספת ההוצאה הבסיסי"""
    #     self.expense_name_field.clear()
    #     self.expense_name_field.send_keys(name)
        
    #     self.amount_field.clear()
    #     self.amount_field.send_keys(amount)
        
    #     # הערה: עבודה מול DatePicker ו-Dropdown דורשת לפעמים לחיצות נוספות, 
    #     # אז בשלב זה נמלא את שדות החובה הטקסטואליים ונשמור.
    #     self.add_expense_button.click()