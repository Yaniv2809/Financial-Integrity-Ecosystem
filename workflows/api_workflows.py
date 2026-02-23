from extensions.api_actions import APIActions
from config.config import ConfigManager

class APIWorkflows:
    """
    מחלקה זו מרכזת את כל הזרימות העסקיות (Business Flows) שקשורות ל-API של מערכת ההוצאות.
    """

    @staticmethod
    def create_expense(description, amount, currency="ILS"):
        """
        זרימה עסקית: יצירת הוצאה חדשה במערכת.
        הפונקציה מושכת את הכתובת, בונה את ה-Payload הנדרש, ושולחת אותו לשרת.
        """
        # משיכת כתובת השרת מתוך קובץ הקונפיגורציה שיצרנו קודם
        base_url = ConfigManager.get_env_data()['api_base_url']
        endpoint = f"{base_url}/expenses"
        
        # יצירת אובייקט הנתונים (מילון) שנישלח לשרת
        payload = {
            "description": description,
            "amount": float(amount),
            "currency": currency
        }
        
        # שימוש במעטפת שיצרנו ב-extensions כדי לבצע בקשת POST
        response = APIActions.post(endpoint, payload)
        return response

    @staticmethod
    def get_all_expenses():
        """
        זרימה עסקית: שליפת כל ההוצאות הקיימות במערכת (GET).
        """
        base_url = ConfigManager.get_env_data()['api_base_url']
        endpoint = f"{base_url}/expenses"
        
        # שימוש במעטפת שיצרנו ב-extensions כדי לבצע בקשת GET
        response = APIActions.get(endpoint)
        return response