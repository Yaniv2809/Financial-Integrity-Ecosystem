import allure
from utils.logger import Logger

log = Logger()

class APIActions:
    
    @staticmethod
    @allure.step("API Action: Sending GET request to {url}")
    def get(session, url, timeout=10):
        log.info(f"API Action: Sending GET request to {url}")
        # שימוש בסשן במקום ב-requests הישיר
        response = session.get(url, timeout=timeout)
        return response

    @staticmethod
    @allure.step("API Action: Sending POST request to {url}")
    def post(session, url, payload, timeout=10):
        log.info(f"API Action: Sending POST request to {url}")
        response = session.post(url, json=payload, timeout=timeout)
        return response

    @staticmethod
    @allure.step("API Action: Sending PUT request to {url}")
    def put(session, url, payload, timeout=10):
        log.info(f"API Action: Sending PUT request to {url}")
        response = session.put(url, json=payload, timeout=timeout)
        return response

    @staticmethod
    @allure.step("API Action: Sending DELETE request to {url}")
    def delete(session, url, timeout=10):
        log.info(f"API Action: Sending DELETE request to {url}")
        response = session.delete(url, timeout=timeout)
        return response