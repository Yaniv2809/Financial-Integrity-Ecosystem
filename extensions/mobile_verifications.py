import allure
import pytest_check as check
from selenium.webdriver.common.by import By

class MobileVerifications:
    
    @staticmethod
    def verify_element_displayed(element, element_name="Element"):
        """
        מוודא שהאלמנט מוצג על המסך - Soft Assert
        """
        # הפונקציה is_true לא תעצור את הטסט אם היא נכשלת
        check.is_true(element.is_displayed(), f'error: element {element_name} is not displayed on screen')
        
    @staticmethod
    def verify_text(element, expected_text, element_name="Element"):
        """
        מוודא שהטקסט בתוך האלמנט תואם לטקסט המצופה - Soft Assert
        """
        actual_text = element.text
        # הפונקציה equal משווה בין הערכים בצורה רכה
        check.equal(actual_text, expected_text, f'error in element {element_name}: expected text "{expected_text}", but got "{actual_text}"')
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