import allure
from extensions.api_actions import APIActions

BASE_URL = "http://localhost:3000/expenses"

class APIWorkflows:

    @staticmethod
    @allure.step("⚙️ Workflow: Get All Expenses")
    def get_all_expenses():
        return APIActions.get(BASE_URL)

    @staticmethod
    @allure.step("⚙️ Workflow: Get Expense by ID: {expense_id}")
    def get_expense_by_id(expense_id):
        return APIActions.get(f"{BASE_URL}/{expense_id}")

    @staticmethod
    @allure.step("⚙️ Workflow: Create New Expense")
    def create_expense(description, amount, date, category):
        payload = {
            "description": description,
            "amount": amount,
            "date": date,
            "category": category
        }
        return APIActions.post(BASE_URL, payload)

    @staticmethod
    @allure.step("⚙️ Workflow: Update Expense ID: {expense_id}")
    def update_expense(expense_id, description, amount, date, category):
        payload = {
            "description": description,
            "amount": amount,
            "date": date,
            "category": category
        }
        return APIActions.put(f"{BASE_URL}/{expense_id}", payload)

    @staticmethod
    @allure.step("⚙️ Workflow: Delete Expense ID: {expense_id}")
    def delete_expense(expense_id):
        return APIActions.delete(f"{BASE_URL}/{expense_id}")