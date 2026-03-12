import requests
import allure
from utils.logger import Logger

log = Logger()

class APIActions:
    
    @staticmethod
    @allure.step("API Action: Sending GET request to {url}")
    def get(url):
        log.info(f"API Action: Sending GET request to {url}")
        response = requests.get(url)
        return response

    @staticmethod
    @allure.step("API Action: Sending POST request to {url}")
    def post(url, payload):
        log.info(f"API Action: Sending POST request to {url}")
        response = requests.post(url, json=payload)
        return response

    @staticmethod
    @allure.step("API Action: Sending PUT request to {url}")
    def put(url, payload):
        log.info(f"API Action: Sending PUT request to {url}")
        response = requests.put(url, json=payload)
        return response

    @staticmethod
    @allure.step("API Action: Sending DELETE request to {url}")
    def delete(url):
        log.info(f"API Action: Sending DELETE request to {url}")
        response = requests.delete(url)
        return response