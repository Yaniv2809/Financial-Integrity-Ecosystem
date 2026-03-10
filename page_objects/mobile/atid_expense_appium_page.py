
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common import appiumby
from selenium.webdriver.common.by import By



class AtidExpenseAppiumPage:
    def __init__(self, driver):
        self.driver = driver
        
        self.name_field = (By.XPATH, "//*[@resource-id='expense-name']") # שיפור: resource-id נפוץ יותר במובייל
        self.amount_field = (By.XPATH, "//*[@resource-id='expense-amount']")
        self.date_field = (By.XPATH, "//*[@resource-id='expense-date']")
        self.category_selector = (By.XPATH, "//*[@text='Select Category']")
        self.add_button = (By.XPATH, "//*[@text='Add Expense']")
        self.ok_button = (By.XPATH, "//*[@resource-id='android:id/button1']")
        self.delete_btn_base = (By.XPATH, "//*[@text='Delete']")
        
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


    def click_delete_by_name(self, name):
        dynamic_xpath = f"//*[contains(@text, '{name}')]/..//*[@text='Delete']"
        self.driver.find_element(By.XPATH, dynamic_xpath).click()    
        #אם מחר המפתח ישנה את המבנה (למשל, כפתור המחיקה כבר לא יהיה תחת אותו "אבא"), את תצטרכי לתקן את זה רק במקום אחד – ב-Page Object.
        #כדי לשמור על encapsulation (כמיסה). ה-Flow לא צריך להכיר את ה-DOM או את ה-XPath, הוא רק צריך לדעת להפעיל שירותים שה-Page Object מספק."
    

