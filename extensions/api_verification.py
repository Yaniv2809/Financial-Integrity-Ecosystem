import allure
import requests

class APIVerifications:
    @staticmethod
    @allure.step(" Verifying response status code is {expected_status}")
    def verify_status_code(response: requests.Response, expected_status: int):
        actual_status = response.status_code
        assert actual_status == expected_status, f" Expected status {expected_status}, but got {actual_status}. Response: {response.text}"