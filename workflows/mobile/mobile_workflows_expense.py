from page_objects.mobile.expense_mobile_page import MobileExpensePage
import allure
import time
from extensions.mobile_verifications import MobileVerifications
from extensions.mobile_actions import MobileActions
from page_objects.mobile.atid_expense_appium_page import AtidExpenseAppiumPage
from selenium.webdriver.common.by import By
from extensions.mobile_verifications import MobileVerify
from extensions.mobile_actions import MobileActions
from selenium.webdriver.common.by import By



class AtidExpenseAppiumFlows:
    def __init__(self, driver):
        self.driver = driver
        self.expense_page = AtidExpenseAppiumPage(driver)

    @allure.step("Flow: Add New Expense")
    def add_expenses(self, name: str, amount: str, day: str, category: str) -> None:
        # 1. הזנת שם וסכום
        MobileActions.update_text(self.driver, self.expense_page.name_field, name)
        MobileActions.update_text(self.driver, self.expense_page.amount_field, amount)
    
        # 2. בחירת תאריך
        MobileActions.click(self.driver, self.expense_page.date_field)
        day_locator = (By.XPATH, f"//*[@text='{day}']")
        MobileActions.click(self.driver, day_locator)
        MobileActions.click(self.driver, self.expense_page.ok_button)
    
        # 3. בחירת קטגוריה - כאן היה התיקון:
        # קודם לוחצים על התפריט עצמו
        MobileActions.click(self.driver, self.expense_page.category_selector)
        
        # אז לוחצים על האופציה הספציפית שרוצים מתוך הרשימה
        category_option = (By.XPATH, f"//*[@text='{category}']")
        MobileActions.click(self.driver, category_option)
    
        # 4. לחיצה על הוספה
        MobileActions.click(self.driver, self.expense_page.add_button)
     #kind of refershing but here using background_app not refresh like web
    @allure.step("Send App To Background")
    def send_app_to_background(self):
        self.driver.background_app(3)

    @allure.step("Flow: Verify Persistence After Background")
    def verify_persistence_flow(self, name: str) -> None:

        # שליחת האפליקציה לרקע
        self.driver.background_app(3)

        # חיפוש ה-expense במסך
        expense_locator = (By.XPATH, f"//*[@text='{name}']")

        # verification
        MobileActions.visible(self.driver, expense_locator)



    def delete_expense_flow(self, name):
        self.expense_page.click_delete_by_name(name)
        # המתנה קצרה של שנייה אחת כדי לאפשר ל-UI להתעדכן
        time.sleep(5)