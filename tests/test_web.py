import pytest
import allure
import requests
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
        WebWorkflows.create_expense(
            page=page, 
            description=description,
            amount=amount, 
            date=date,
            category=category
            
        )

        WebVerify.contain_text(page.locator("[class='expense-name']").last, description)
        WebVerify.contain_text(page.locator("[class='expense-amount']").last, str(amount))
        WebVerify.contain_text(page.locator("[class='expense-date']").last, date)
        WebVerify.contain_text(page.locator("[class='expense-category']").last, category)

    @allure.title("Verify expense list count")
    @allure.description("This test verifies that adding new expenses properly increases the total number of items in the DOM")
    def test03_verify_expense_list_count(self):

        initial_count = page.locator(".expense-name").count()
        print(f"\nCurrent expenses count: {initial_count}")
        
        WebWorkflows.create_expense(page, description="Coffee", amount=15, category="Food", date="2025-06-01")
        WebWorkflows.create_expense(page, description="Bus ticket", amount=10, category="Transportation", date="2025-06-02")

        expected_new_count = initial_count + 2
        WebVerify.verify_element_count(page.locator("[class='expense-name']"), expected_new_count)
        
        print(f"Verified new count is exactly: {expected_new_count}")


    @allure.title("Verify expense creation with real-time API conversion")
    @allure.description("Fetches real-time USD to ILS conversion rate via API, calculates the expense, and adds it via UI")
    def test04_verify_expense_with_api_rate(self):
        # 1. משיכת שער הדולר הנוכחי מ-API חינמי באינטרנט
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        data = response.json()
        
        # שולפים את שער השקל מתוך הנתונים שקיבלנו (למשל 3.75)
        ils_rate = data['rates']['ILS']
        
        # 2. חישוב ההוצאה: 100 דולר בשקלים (מעגלים ל-2 ספרות אחרי הנקודה)
        usd_amount = 100
        calculated_ils = round(usd_amount * ils_rate, 2)
        
        description = f"Business Trip NY ({usd_amount} USD)"
        print(f"\nReal-time ILS Rate: {ils_rate}. Converted Amount: {calculated_ils} ILS")
        
        # 3. ביצוע הפעולה באתר (הזרקת הנתון המחושב לתוך ה-UI!)
        WebWorkflows.create_expense(
            page=page, 
            description=description, 
            amount=calculated_ils, 
            category="Transportation", 
            date="2025-06-10"
        )
        
        # 4. אימות שהמערכת שמרה והציגה את הסכום המדויק שחישבנו מול ה-API
        WebVerify.contain_text(page.locator(".expense-name").last, description)
        WebVerify.contain_text(page.locator(".expense-amount").last, str(calculated_ils))