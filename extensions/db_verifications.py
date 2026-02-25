import allure

class DBVerifications:
    
    @staticmethod
    @allure.step(" Verifying DB returned exactly {expected_count} records")
    def verify_record_count(records: list, expected_count: int):
        actual_count = len(records)
        assert actual_count == expected_count, f" Expected {expected_count} records, but got {actual_count}."