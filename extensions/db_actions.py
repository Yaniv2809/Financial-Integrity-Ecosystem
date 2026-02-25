import sqlite3
import allure

class DBActions:
    
    @staticmethod
    @allure.step("🗄️ Executing DB Query: {query}")
    def execute_query(db_path: str, query: str, params: tuple = ()) -> list:
        """
        פונקציה חכמה שיודעת גם להחזיר נתונים (SELECT) וגם לשמור שינויים (INSERT/UPDATE).
        """
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            
            # הרצת השאילתה עם פרמטרים (למניעת SQL Injection)
            cursor.execute(query, params)
            
            # אם זו שאיבת נתונים
            if query.strip().upper().startswith("SELECT"):
                records = cursor.fetchall()
                allure.attach(str(records), name="DB Results", attachment_type=allure.attachment_type.TEXT)
                return records
            
            # אם זו כתיבת נתונים
            else:
                connection.commit()
                return []
                
        except sqlite3.Error as error:
            print(f"❌ DB Error: {error}")
            raise error
            
        finally:
            if connection:
                connection.close()