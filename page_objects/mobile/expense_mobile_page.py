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

    

