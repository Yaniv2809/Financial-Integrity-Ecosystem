import pytest_check as check

class MobileVerifications:
    
    @staticmethod
    def verify_element_displayed(element, element_name="Element"):
        """
        מוודא שהאלמנט מוצג על המסך - Soft Assert
        """
        # הפונקציה is_true לא תעצור את הטסט אם היא נכשלת
        check.is_true(element.is_displayed(), f'error: element {element_name} is not displayed on screen')
        
    @staticmethod
    def verify_text(element, expected_text, element_name="Element"):
        """
        מוודא שהטקסט בתוך האלמנט תואם לטקסט המצופה - Soft Assert
        """
        actual_text = element.text
        # הפונקציה equal משווה בין הערכים בצורה רכה
        check.equal(actual_text, expected_text, f'error in element {element_name}: expected text "{expected_text}", but got "{actual_text}"')