import allure
from utils.logger import Logger

log = Logger()


class UIActions:
    """
    מחלקה זו עוטפת את כל הפעולות הטכניות של הדפדפן (UI).
    כל פעולה מתועדת אוטומטית ב-Logger וב-Allure.
    """

    @staticmethod
    @allure.step("Navigate to URL: {url}")
    def navigate(page, url):
        log.info(f"UI Action: Navigating to URL: {url}")
        page.goto(url)

    @staticmethod
    @allure.step("UI Action: Clicking on element: '{selector}'")
    def click(page, selector: str, is_last: bool = False):
        log.info(f"UI Action: Clicking on element with selector: '{selector}'")
        if is_last:
            page.locator(selector).last.click()
        else:
            page.locator(selector).click()

    @staticmethod
    @allure.step("Fill text: '{text}' into element: {selector}")
    def fill_text(page, selector, text):
        log.info(f"UI Action: Typing '{text}' into element with selector: '{selector}'")
        page.locator(selector).fill(text)

    @staticmethod
    @allure.step("Get text from element: {selector}")
    def get_text(page, selector):
        log.info(f"UI Action: Extracting text from element with selector: '{selector}'")
        return page.locator(selector).inner_text()

    @staticmethod
    @allure.step("Select option: '{option}' in element: {selector}")
    def select_option(page, selector, option):
        log.info(f"UI Action: Selecting '{option}' in dropdown with selector: '{selector}'")
        page.locator(selector).select_option(label=option)
    
