"""
Flask REST API server backed by SQLite or MySQL.
Replaces json-server to enable real data integrity testing:
API calls actually write to/read from the configured database.
"""
import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, abort

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_test.db")


def _get_db_type():
    """Reads DB type from env var (priority) or config.json fallback."""
    db_type = os.environ.get("DB_TYPE")
    if db_type:
        return db_type.lower()
    try:
        import json
        config_path = os.path.join(PROJECT_ROOT, "config", "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("db_type", "sqlite").lower()
    except Exception:
        return "sqlite"


def get_db():
    db_type = _get_db_type()
    if db_type == "mysql":
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", 3306)),
            user=os.environ.get("MYSQL_USER", "test_user"),
            password=os.environ.get("MYSQL_PASSWORD", "test_password"),
            database=os.environ.get("MYSQL_DATABASE", "expense_test_db"),
        )
        return conn
    else:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    db_type = _get_db_type()
    if db_type == "mysql":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INT PRIMARY KEY AUTO_INCREMENT,
                expense_name VARCHAR(255),
                amount DOUBLE,
                date VARCHAR(50),
                category VARCHAR(100)
            )
        """)
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_name TEXT,
                amount REAL,
                date TEXT,
                category TEXT
            )
        """)
        conn.commit()
        conn.close()


def _query(conn, sql, params=None):
    """Execute a query with the right placeholder format."""
    db_type = _get_db_type()
    if db_type == "mysql":
        sql = sql.replace("?", "%s")
    cursor = conn.cursor() if db_type == "mysql" else conn
    if params:
        result = cursor.execute(sql, params)
    else:
        result = cursor.execute(sql)
    return cursor if db_type == "mysql" else result


def _fetchone(conn, sql, params=None):
    db_type = _get_db_type()
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql.replace("?", "%s"), params or ())
        return cursor.fetchone()
    else:
        return conn.execute(sql, params or ()).fetchone()


def _fetchall(conn, sql, params=None):
    db_type = _get_db_type()
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql.replace("?", "%s"), params or ())
        return cursor.fetchall()
    else:
        return conn.execute(sql, params or ()).fetchall()


def validate_expense(data):
    """מאמת את הנתונים ומחזיר רשימת שגיאות"""
    errors = []

    # expense_name validation
    name = data.get("expense_name") or data.get("description") or ""
    if not name or not str(name).strip():
        errors.append("expense_name is required and cannot be empty or spaces-only")
    elif len(str(name)) > 200:
        errors.append(f"expense_name too long ({len(str(name))} chars, max 200)")

    # amount validation
    amount = data.get("amount")
    if amount is None:
        errors.append("amount is required")
    else:
        try:
            amount_float = float(amount)
            if amount_float < 0:
                errors.append(f"amount cannot be negative ({amount_float})")
            if amount_float == 0:
                errors.append("amount cannot be zero")
        except (ValueError, TypeError):
            errors.append(f"amount must be numeric, got: {amount}")

    # date validation
    date = data.get("date", "")
    if not date:
        errors.append("date is required")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"date must be YYYY-MM-DD format, got: {date}")

    # category validation
    valid_categories = ["Food", "Transportation", "Accommodation", "Education", "Fashion", "Other"]
    category = data.get("category", "")
    if not category:
        errors.append("category is required")
    elif category not in valid_categories:
        errors.append(f"Invalid category '{category}'. Must be one of: {valid_categories}")

    return errors


@app.route("/health", methods=["GET"])
def health():
    """בדיקת בריאות השרת וחיבור ל-DB"""
    db_status = "disconnected"
    record_count = 0
    try:
        conn = get_db()
        row = _fetchone(conn, "SELECT COUNT(*) as cnt FROM expenses")
        record_count = row["cnt"] if isinstance(row, dict) else row[0]
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "record_count": record_count,
    })


def row_to_dict(row):
    if isinstance(row, dict):
        return row
    return {
        "id": row["id"],
        "expense_name": row["expense_name"],
        "amount": row["amount"],
        "date": row["date"],
        "category": row["category"],
    }


@app.route("/expenses", methods=["GET"])
def get_expenses():
    conn = get_db()
    try:
        rows = _fetchall(conn, "SELECT * FROM expenses")
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    conn = get_db()
    try:
        row = _fetchone(conn, "SELECT * FROM expenses WHERE id = ?", (expense_id,))
        if row is None:
            abort(404)
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.route("/expenses", methods=["POST"])
def create_expense():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    errors = validate_expense(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    conn = get_db()
    try:
        db_type = _get_db_type()
        sql = "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)"
        params = (
            data.get("expense_name") or data.get("description"),
            data.get("amount"),
            data.get("date"),
            data.get("category"),
        )

        if db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql.replace("?", "%s"), params)
            conn.commit()
            new_id = cursor.lastrowid
        else:
            cursor = conn.execute(sql, params)
            conn.commit()
            new_id = cursor.lastrowid

        row = _fetchone(conn, "SELECT * FROM expenses WHERE id = ?", (new_id,))
        return jsonify(row_to_dict(row)), 201
    finally:
        conn.close()


@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    errors = validate_expense(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    conn = get_db()
    try:
        sql = "UPDATE expenses SET expense_name=?, amount=?, date=?, category=? WHERE id=?"
        params = (
            data.get("expense_name") or data.get("description"),
            data.get("amount"),
            data.get("date"),
            data.get("category"),
            expense_id,
        )

        db_type = _get_db_type()
        if db_type == "mysql":
            cursor = conn.cursor()
            cursor.execute(sql.replace("?", "%s"), params)
        else:
            conn.execute(sql, params)
        conn.commit()

        row = _fetchone(conn, "SELECT * FROM expenses WHERE id = ?", (expense_id,))
        if row is None:
            abort(404)
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = get_db()
    try:
        db_type = _get_db_type()
        sql = "DELETE FROM expenses WHERE id = ?"
        if db_type == "mysql":
            cursor = conn.cursor()
            cursor.execute(sql.replace("?", "%s"), (expense_id,))
        else:
            conn.execute(sql, (expense_id,))
        conn.commit()
        return jsonify({}), 200
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
