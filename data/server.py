import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# עולים שתי רמות: מהקובץ -> לתיקיית server -> לתיקייה הראשית של הפרויקט
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_db.db")

def get_db_connection():
    """פותח חיבור אמיתי ל-DB"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/expenses', methods=['POST'])
def create_expense():
    """יצירת הוצאה - כותב באמת ל-SQLite!"""
    data = request.get_json()
    
    # מתרגמים את 'description' מה-API ל-'expense_name' של ה-DB
    name = data.get('description') or data.get('expense_name')
    amount = data.get('amount')
    date = data.get('date')
    category = data.get('category')

    # ולידציה בסיסית - לא נותנים להכניס זבל
    if not name or amount is None:
        return jsonify({"error": "Missing required fields: name or amount"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # פקודת ההכנסה האמיתית
        cursor.execute(
            "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)",
            (name, float(amount), date, category)
        )
        conn.commit() # החלק הכי חשוב שהיה חסר לכם! שומר את המידע בדיסק!
        expense_id = cursor.lastrowid
        
    except sqlite3.IntegrityError as e:
        conn.rollback() # במקרה של שגיאה (כמו חסר שדה חובה), מבטלים
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        conn.close()

    # מחזירים 201 רק אחרי שהמידע באמת נשמר!
    return jsonify({"id": expense_id, "message": "Expense created successfully in DB"}), 201

@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """שליפת הוצאה מה-DB"""
    conn = get_db_connection()
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    
    if expense is None:
        return jsonify({"error": "Expense not found"}), 404
        
    return jsonify({
        "id": expense["id"],
        "description": expense["expense_name"], # מחזירים description כדי לא לשבור לך את הטסטים
        "amount": expense["amount"],
        "date": expense["date"],
        "category": expense["category"]
    }), 200

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """מחיקת הוצאה מה-DB (בשביל ה-Cleanup של הטסטים)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    if deleted == 0:
        return jsonify({"error": "Expense not found"}), 404
        
    return jsonify({"message": "Expense deleted"}), 200

if __name__ == '__main__':
    print(f"🚀 Starting Real Backend. Connected to DB at: {DB_PATH}")
    app.run(port=5000, debug=True)