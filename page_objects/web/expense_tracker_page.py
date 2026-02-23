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