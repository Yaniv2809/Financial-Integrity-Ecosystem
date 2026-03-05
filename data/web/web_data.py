import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EXPENSES_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "ddt", "expenses_data.csv")

EXPENSES_2_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "ddt", "expense_2_data.csv")