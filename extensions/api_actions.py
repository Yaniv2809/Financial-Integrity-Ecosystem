import requests
import allure

class APIActions:
    
    @staticmethod
    @allure.step("API Action: Sending GET request to {url}")
    def get(url):
        response = requests.get(url)
        return response

    @staticmethod
    @allure.step("API Action: Sending POST request to {url}")
    def post(url, payload):
        response = requests.post(url, json=payload)
        return response

    @staticmethod
    @allure.step("API Action: Sending PUT request to {url}")
    def put(url, payload):
        response = requests.put(url, json=payload)
        return response

    @staticmethod
    @allure.step("API Action: Sending DELETE request to {url}")
    def delete(url):
        response = requests.delete(url)
        return response