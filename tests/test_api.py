import pytest
import allure
from workflows.api.api_workflows import APIWorkflows
from extensions.verifications import Verifications

class TestAPI:
    """
    מחלקת הבדיקות עבור פלטפורמת ה-API.
    הטסטים כתובים ברמה עסקית בלבד, ללא לוגיקה טכנית מורכבת.
    """

    @allure.title("Create a new expense via API")
    @allure.description("This test verifies that a new expense can be successfully created in the system using the API")
    def test01_create_expense(self):
        # שלב 1: ביצוע הפעולה העסקית
        response = APIWorkflows.create_expense(description="Food", amount=190)
        
        Verifications.verify_equals(response.status_code, 201, "Expected status code 201 (Created)")
        
        response_data = response.json()
        Verifications.verify_equals(response_data["description"], "Food", "Description does not match!")
        Verifications.verify_equals(response_data["amount"], 190, "Amount does not match!")
        Verifications.verify_contains(response_data, "id", "Response missing an 'id' field!")