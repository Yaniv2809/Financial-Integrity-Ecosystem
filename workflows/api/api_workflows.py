import allure
from extensions.api_actions import APIActions
from config.config import ConfigManager

class APIWorkflows:

    @staticmethod
    @allure.step("⚙️ Workflow: Get All Expenses")
    def get_all_expenses():
        url = ConfigManager.get_env_data()['api_url']
        return APIActions.get(url)

    @staticmethod
    @allure.step("⚙️ Workflow: Get Expense by ID: {expense_id}")
    def get_expense_by_id(expense_id):
        url = ConfigManager.get_env_data()['api_url']
        return APIActions.get(f"{url}/{expense_id}")

    @staticmethod
    @allure.step("⚙️ Workflow: Create New Expense")
    def create_expense(description, amount, date, category):
        url = ConfigManager.get_env_data()['api_url']
        payload = {
            "description": description,
            "amount": amount,
            "date": date,
            "category": category
        }
        return APIActions.post(url, payload)

    @staticmethod
    @allure.step("⚙️ Workflow: Update Expense ID: {expense_id}")
    def update_expense(expense_id, description, amount, date, category):
        url = ConfigManager.get_env_data()['api_url']
        payload = {
            "description": description,
            "amount": amount,
            "date": date,
            "category": category
        }
        return APIActions.put(f"{url}/{expense_id}", payload)

    @staticmethod
    @allure.step("⚙️ Workflow: Delete Expense ID: {expense_id}")
    def delete_expense(expense_id):
        url = ConfigManager.get_env_data()['api_url']
        return APIActions.delete(f"{url}/{expense_id}")