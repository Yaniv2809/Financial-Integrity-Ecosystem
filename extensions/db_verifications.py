import allure
from smart_assertions import soft_assert

class DBVerifications:
    
    @staticmethod
    @allure.step(" Verifying DB returned exactly {expected_count} records")
    def verify_record_count(records: list, expected_count: int):
        actual_count = len(records)
        assert actual_count == expected_count, f" Expected {expected_count} records, but got {actual_count}."

    @staticmethod
    @allure.step("Verifying DB record data matches expected data")
    def verify_db_record_match(actual_record: tuple, expected_record: tuple):
        db_expense_name, db_amount, db_category = actual_record
        expected_name, expected_amount, expected_category = expected_record
        
        soft_assert(db_expense_name == expected_name, f"Name mismatch: Expected '{expected_name}', got '{db_expense_name}'")
        soft_assert(float(db_amount) == float(expected_amount), f"Amount mismatch: Expected '{expected_amount}', got '{db_amount}'")
        soft_assert(db_category == expected_category, f"Category mismatch: Expected '{expected_category}', got '{db_category}'")