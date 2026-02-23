import allure
from utils.logger import Logger

class Verifications:
    """
    מחלקה זו מרכזת את כל פעולות האימות (Assertions) בפרויקט.
    היא מוודאת שכל אימות מתועד גם ללוגר וגם לדוח ה-Allure.
    """
    @staticmethod
    @allure.step("Verify Equals: {actual} == {expected}")
    def verify_equals(actual, expected, message="Verification failed"):
        log = Logger()
        try:
            assert actual == expected, message
            log.info(f"Verification Passed: {actual} equals {expected}")
        except AssertionError as e:
            log.error(f"Verification Failed: {actual} does not equal {expected}. Error: {e}")
            raise e

    @staticmethod
    @allure.step("Verify Contains: '{expected}' in '{actual}'")
    def verify_contains(actual, expected, message="Verification failed"):
        log = Logger()
        try:
            assert expected in actual, message
            log.info(f"Verification Passed: '{expected}' is found in '{actual}'")
        except AssertionError as e:
            log.error(f"Verification Failed: '{expected}' not found in '{actual}'. Error: {e}")
            raise e