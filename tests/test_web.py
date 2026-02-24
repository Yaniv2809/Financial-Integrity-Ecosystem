import pytest
import allure
from playwright.sync_api import Playwright
from workflows.web.web_workflows import WebWorkflows
from config.config import ConfigManager
from extensions.ui_actions import UIActions
from extensions.web_verification import WebVerify

class TestWeb:
    @pytest.fixture(autouse=True, scope="class")
    def setup(self, playwright: Playwright):
        global browser, context, page
  
        browser = playwright.chromium.launch(headless=False, channel="chrome", slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        url = ConfigManager.get_env_data()['web_url']
        page.goto(url)
    
        yield
        
        context.close()
        page.close()

    @allure.title("Create a new expense via Web UI")
    @allure.description("This test verifies that a new expense can be added to the tracker")
    def test01_create_expense_web(self):
        WebWorkflows.create_expense(
            page=page, 
            description="Business Lunch Web", 
            amount=150, 
            date="2025-05-20",
            category="Food"
            
        )
        WebVerify.contain_text(page.locator(".expense-name"), "Business Lunch Web")
        WebVerify.contain_text(page.locator(".expense-amount"), "150")
        WebVerify.contain_text(page.locator(".expense-date"), "2025-05-20")
        WebVerify.contain_text(page.locator(".expense-category"), "Food")

    expense_data = [
        ("Taxi to office", 50, "Transportation", "2025-05-21"),
        ("Client Dinner", 320, "Food", "2025-05-22"),
        ("New Monitor", 850, "Accommodation", "2025-05-23")
    ]

    @allure.title("Create multiple expenses via DDT")
    @allure.description("This test uses Data-Driven Testing to add several expenses one after another")
    @pytest.mark.parametrize("description, amount, category, date", expense_data)
    def test02_create_multiple_expenses_ddt(self, description, amount, category, date):
        # 1. ביצוע הפעולה - הפעם אנחנו מעבירים את המשתנים שמגיעים מהרשימה!
        WebWorkflows.create_expense(
            page=page, 
            description=description,
            amount=amount, 
            date=date,
            category=category
            
        )
        # 2. אימות - נבדוק שההוצאה החדשה אכן מופיעה ברשימה עם הפרטים הנכונים
        WebVerify.contain_text(page.locator("[class='expense-name']").last, description)
        WebVerify.contain_text(page.locator("[class='expense-amount']").last, str(amount))
        WebVerify.contain_text(page.locator("[class='expense-date']").last, date)
        WebVerify.contain_text(page.locator("[class='expense-category']").last, category)

    