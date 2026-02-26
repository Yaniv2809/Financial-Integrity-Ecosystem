import allure

class APIVerifications:

    @staticmethod
    @allure.step("✅ API Verify: Status Code is {expected_status}")
    def verify_status_code(response, expected_status):
        assert response.status_code == expected_status, \
            f"❌ Expected status {expected_status}, but got {response.status_code}"

    @staticmethod
    @allure.step("✅ API Verify: Response key '{key}' contains '{expected_value}'")
    def verify_response_value(response, key, expected_value):
        actual_value = response.json().get(key)
        assert actual_value == expected_value, \
            f"❌ Expected '{key}' to be {expected_value}, but got {actual_value}"