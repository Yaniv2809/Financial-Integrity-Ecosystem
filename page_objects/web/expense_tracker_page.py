


class ExpenseTrackerPage:
    """
    Page Object Model (POM) עבור דף ניהול ההוצאות ב-Web.
    מכיל רק את הסלקטורים של האתר.
    """
    
    expense_name = "input[id='expense-name']"      # שדה תיאור ההוצאה
    txt_amount = "input[id='expense-amount']"         # שדה סכום ההוצאה
    category_dropdown = "select[id='expense-category']" # תפריט בחירת קטגוריה
    add_date = "input[id='expense-date']"              # שדה תאריך ההוצאה
    btn_add = "button[id='add-expense']"              # כפתור הוספת הוצאה
    list_expense_rows = "#expense-list li"            # שורות הטבלה (לאימות נתונים)
    delete_buttons = "//*[@id='expense-list']//button"     # כפתורי מחיקה (לאימות מחיקה)
    expense_list = "[id='expense-list']"                         # רשימת ההוצאות)
    #list elements for verification
    expense_name_items = ".expense-name"          # שמות ההוצאות ברשימה
    expense_amount_items = ".expense-amount"      # סכומי ההוצאות ברשימה
    expense_date_items = ".expense-date"          # תאריכי ההוצאות ברשימה
    expense_category_items = ".expense-category"  # קטגוריות ההוצאות ברשימה


    non_existent_ai_button = "#non-existent-button-for-ai-test"


    @staticmethod
    def get_last_expense_name(page):
        return page.locator(ExpenseTrackerPage.expense_name_items).last
    
    @staticmethod
    def get_last_expense_elements(page):
        """
        תופס את הרשומה האחרונה ברשימה, ומחזיר מילון של כל הלוקייטורים בתוכה.
        """
        last_item = page.locator("#expense-list li").last

        return {
            "name": last_item.locator(".expense-name"),
            "amount": last_item.locator(".expense-amount"),
            "date": last_item.locator(".expense-date"),
            "category": last_item.locator(".expense-category"),
        }
    
    @staticmethod
    def get_expenses_count(page) -> int:
        # במידת הצורך אפשר להוסיף כאן page.wait_for_selector כדי למנוע flakiness
        return page.locator(ExpenseTrackerPage.expense_name_items).count()