import pytest
from utils.logger import Logger

@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    # ------------------ SETUP ------------------
    log = Logger()
    log.info("====== SETUP: Starting Test Execution ======")
    
    yield  
    
    # ----------------- TEARDOWN -----------------
    log.info("====== TEARDOWN: Test Execution Completed ======")
    # AI can add any cleanup code here if needed in the future (e.g., closing database connections, clearing test data, etc.)