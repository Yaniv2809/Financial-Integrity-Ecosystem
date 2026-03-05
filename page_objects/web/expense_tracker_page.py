


class ExpenseTrackerPage:
    """
    Page Object Model (POM) עבור דף ניהול ההוצאות ב-Web.
    מכיל רק את הסלקטורים של האתר.
    """
    
    txt_description = "input[id='expense-name']"      # שדה תיאור ההוצאה
    txt_amount = "input[id='expense-amount']"         # שדה סכום ההוצאה
    category_dropdown = "select[id='expense-category']" # תפריט בחירת קטגוריה
    add_date = "input[id='expense-date']"              # שדה תאריך ההוצאה
    btn_add = "button[id='add-expense']"              # כפתור הוספת הוצאה
    list_expense_rows = "tbody tr"            # שורות הטבלה (לאימות נתונים)
    delete_buttons = "//*[@id='expense-list']//button"     # כפתורי מחיקה (לאימות מחיקה)
    expanse_list = "[id='expense-list']"                         # רשימת ההוצאות)
    #list elements for verification
    expense_name_items = ".expense-name"          # שמות ההוצאות ברשימה
    expense_amount_items = ".expense-amount"      # סכומי ההוצאות ברשימה
    expense_date_items = ".expense-date"          # תאריכי ההוצאות ברשימה
    expense_category_items = ".expense-category"  # קטגוריות ההוצאות ברשימה



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