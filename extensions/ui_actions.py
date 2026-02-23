import allure
from utils.logger import Logger

class UIActions:
    """
    מחלקה זו עוטפת את כל הפעולות הטכניות של הדפדפן (UI).
    המטרה: כל קליק או הקלדה מתועדים אוטומטית גם ללוגר וגם לדוחות של Allure.
    אנו מעבירים את אובייקט ה-page של Playwright לכל פונקציה כדי לבצע את הפעולה.
    """

    @staticmethod
    @allure.step("Navigate to URL: {url}")
    def navigate(page, url):
        log = Logger()
        log.info(f"UI Action: Navigating to URL: {url}")
        page.goto(url)

    @staticmethod
    @allure.step("Click on element: {selector}")
    def click(page, selector):
        log = Logger()
        log.info(f"UI Action: Clicking on element with selector: '{selector}'")
        page.locator(selector).click()

    @staticmethod
    @allure.step("Fill text: '{text}' into element: {selector}")
    def fill_text(page, selector, text):
        log = Logger()
        log.info(f"UI Action: Typing '{text}' into element with selector: '{selector}'")
        page.locator(selector).fill(text)

    @staticmethod
    @allure.step("Get text from element: {selector}")
    def get_text(page, selector):
        log = Logger()
        log.info(f"UI Action: Extracting text from element with selector: '{selector}'")
        return page.locator(selector).inner_text()
    
    @staticmethod
    @allure.step("Select option: '{option}' in element: {selector}")
    def select_option(page, selector, option):
        log = Logger()
        log.info(f"UI Action: Selecting '{option}' in dropdown with selector: '{selector}'")
        # פקודה מיוחדת של Playwright לבחירה מתוך תפריט נפתח לפי הערך שלו
        page.locator(selector).select_option(label=option)