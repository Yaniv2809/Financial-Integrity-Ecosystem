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
    @allure.step("Click on element: '{selector}'")
    def click(page, selector: str, is_last: bool = False, **kwargs):
        """
        Clicks an element based on a selector.
        Accepts any valid Playwright click arguments via **kwargs (e.g., timeout=2000, force=True).
        """
        locator = page.locator(selector)
        
        if is_last:
            locator.last.click(**kwargs)
        else:
            locator.click(**kwargs)

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

    @staticmethod
    @allure.step("Clear field: {selector}")
    def clear_field(page, selector):
        field = page.locator(selector)
        if field.input_value():
            field.clear()
    
