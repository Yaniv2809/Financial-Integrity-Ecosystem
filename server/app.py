"""
Flask REST API server backed by SQLite.
Replaces json-server to enable real data integrity testing:
API calls actually write to/read from expense_db.db.
"""
import os
import sqlite3
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "expense_test.db")


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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


def row_to_dict(row):
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
        rows = conn.execute("SELECT * FROM expenses").fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if row is None:
            abort(404)
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.route("/expenses", methods=["POST"])
def create_expense():
    data = request.get_json(force=True)
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO expenses (expense_name, amount, date, category) VALUES (?, ?, ?, ?)",
            (
                data.get("expense_name") or data.get("description"),
                data.get("amount"),
                data.get("date"),
                data.get("category"),
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (new_id,)).fetchone()
        return jsonify(row_to_dict(row)), 201
    finally:
        conn.close()


@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json(force=True)
    conn = get_db()
    try:
        conn.execute(
            "UPDATE expenses SET expense_name=?, amount=?, date=?, category=? WHERE id=?",
            (
                data.get("expense_name") or data.get("description"),
                data.get("amount"),
                data.get("date"),
                data.get("category"),
                expense_id,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if row is None:
            abort(404)
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return jsonify({}), 200
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)