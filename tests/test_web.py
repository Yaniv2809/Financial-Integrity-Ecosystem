import pytest
import allure
import requests
from utils.common_ops import read_data_from_csv
from playwright.sync_api import Playwright
from page_objects.web.expense_tracker_page import ExpenseTrackerPage
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

        WebVerify.contain_text(page.locator(".expense-name").last, "Business Lunch Web")
        WebVerify.contain_text(page.locator(".expense-amount").last, "150")
        WebVerify.contain_text(page.locator(".expense-date").last, "2025-05-20")
        WebVerify.contain_text(page.locator(".expense-category").last, "food") # <-- שים לב לאותיות קטנות!

    expense_data = [
        ("Taxi to office", 50, "Transportation", "2025-05-21"),
        ("Client Dinner", 320, "Food", "2025-05-22"),
        ("New Monitor", 850, "Accommodation", "2025-05-23")
    ]

    EXPENSES_DATA_PATH = r"data\ddt\expenses_data.csv"
    @allure.title("Create multiple expenses via DDT")
    @allure.description("This test uses Data-Driven Testing to add several expenses, reading from an external CSV file")
    @pytest.mark.parametrize("expense_data", read_data_from_csv(EXPENSES_DATA_PATH))
    def test02_create_multiple_expenses_ddt(self, expense_data):

        WebWorkflows.create_expense(
            page=page, 
            description=expense_data["description"],
            amount=expense_data["amount"], 
            date=expense_data["date"],
            category=expense_data["category"]  
        )
        
        WebVerify.contain_text(page.locator(".expense-name").last, expense_data["description"])
        WebVerify.contain_text(page.locator(".expense-amount").last, str(expense_data["amount"]))
        WebVerify.contain_text(page.locator(".expense-date").last, expense_data["date"])
        WebVerify.contain_text(page.locator(".expense-category").last, expense_data["category"].lower())
    
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
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        data = response.json()
        
        ils_rate = data['rates']['ILS']
        
        usd_amount = 100
        calculated_ils = round(usd_amount * ils_rate, 2)
        
        description = f"Business Trip NY ({usd_amount} USD)"
        print(f"\nReal-time ILS Rate: {ils_rate}. Converted Amount: {calculated_ils} ILS")
        
        WebWorkflows.create_expense(
            page=page, 
            description=description, 
            amount=calculated_ils, 
            category="Transportation", 
            date="2025-06-10"
        )

        WebVerify.contain_text(page.locator(".expense-name").last, description)
        WebVerify.contain_text(page.locator(".expense-amount").last, str(calculated_ils))


    @allure.title("Verify creation of expense with negative amount is prevented")
    @allure.description("Negative test: Tries to add an expense with a negative amount (-50) and verifies it fails or isn't added")
    def test05_negative_amount_validation(self):
        # 1. בודקים כמה הוצאות יש כרגע (כדי לוודא שלא תתווסף אחת חדשה)
        initial_count = page.locator(".expense-name").count()
        
        # 2. ניסיון לבצע פעולה אסורה: סכום שלילי
        WebWorkflows.create_expense(page, description="Negative Test", amount=-50)
        
        # 3. אימות - מוודאים שההוצאה *לא* נוספה, כלומר הכמות נשארה בדיוק אותו הדבר
        WebVerify.verify_element_count(page.locator(".expense-name"), initial_count)

    
    @allure.title("Verify deletion of an expense")
    @allure.description("Adds a temporary expense, clicks its delete button, and verifies it is removed from the list")
    def test06_delete_expense(self):
        # 1. יצירת הוצאה זמנית שמיועדת למחיקה
        expense_name = "To Be Deleted"
        WebWorkflows.create_expense(page, description=expense_name, amount=99)
        
        # 2. שמירת כמות האלמנטים *לפני* המחיקה
        count_before_delete = page.locator(".expense-name").count()
        print(f"\nCount before delete: {count_before_delete}")
        
        # 3. לחיצה על כפתור המחיקה של ההוצאה האחרונה שהוספנו
        # משתמשים בסלקטור שהגדרת ב-ExpenseTrackerPage!
        UIActions.click(page, ExpenseTrackerPage.delete_buttons, is_last=True)
        
        # 4. אימות - מוודאים שהכמות הכוללת ירדה ב-1
        expected_count_after = count_before_delete - 1
        WebVerify.verify_element_count(page.locator(".expense-name"), expected_count_after)
        print(f"Count after delete verified as: {expected_count_after}")