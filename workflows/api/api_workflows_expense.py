import allure
from extensions.api_actions import APIActions
from config.config import ConfigManager

class APIWorkflows:

    @staticmethod
    @allure.step("Workflow: Get All Expenses")
    def get_all_expenses(session):
        url = ConfigManager.get_env_data()['api_url']
        # מעבירים את ה-session פנימה לשכבת ה-Actions
        return APIActions.get(session, url)

    @staticmethod
    @allure.step("Workflow: Get Expense by ID: {expense_id}")
    def get_expense_by_id(session, expense_id):
        url = ConfigManager.get_env_data()['api_url']
        return APIActions.get(session, f"{url}/{expense_id}")

    @staticmethod
    @allure.step("Workflow: Create New Expense")
    def create_expense(session, expense_name, amount, date, category):
        url = ConfigManager.get_env_data()['api_url']
        payload = {
            "expense_name": expense_name,
            "amount": amount,
            "date": date,
            "category": category
        }
        return APIActions.post(session, url, payload)

    @staticmethod
    @allure.step("Workflow: Update Expense ID: {expense_id}")
    def update_expense(session, expense_id, expense_name, amount, date, category):
        url = ConfigManager.get_env_data()['api_url']
        payload = {
            "expense_name": expense_name,
            "amount": amount,
            "date": date,
            "category": category
        }
        return APIActions.put(session, f"{url}/{expense_id}", payload)

    @staticmethod
    @allure.step("Workflow: Delete Expense ID: {expense_id}")
    def delete_expense(session, expense_id):
        url = ConfigManager.get_env_data()['api_url']
        return APIActions.delete(session, f"{url}/{expense_id}")