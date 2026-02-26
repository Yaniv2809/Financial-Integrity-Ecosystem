# import pytest
# from utils.logger import Logger

# @pytest.fixture(scope="function", autouse=True)
# def setup_teardown():
#     # ------------------ SETUP ------------------
#     log = Logger()
#     log.info("====== SETUP: Starting Test Execution ======")
    
#     yield  
    
#     # ----------------- TEARDOWN -----------------
#     log.info("====== TEARDOWN: Test Execution Completed ======")
#     # AI can add any cleanup code here if needed in the future (e.g., closing database connections, clearing test data, etc.)

import json
import os
import pytest
from pytest import FixtureRequest
from playwright.sync_api import Playwright
from config.config import ConfigManager
from data.api.api_expense_data import *
from data.web.web_expense_data import *
from utils.fixture_helpers import get_browser
from workflows.api.api_workflows import APIWorkflows
from workflows.web.web_workflows import WebWorkflows

def load_config():
    """Loads the configuration from config.json and returns it as a dictionary."""
    # Get the absolute path of the current directory where conftest.py is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Construct the correct path for config.json (move up one level if necessary)
    CONFIG_PATH = os.path.join(BASE_DIR, "../config/config.json")

    print(f"DEBUG: Looking for config.json at {CONFIG_PATH}")

    # Load the configuration from config.json
    try:
        with open(CONFIG_PATH, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"ERROR: Could not find config.json {CONFIG_PATH}") from e
    
# Load the configuration
CONFIG = load_config()     

@pytest.fixture(autouse=True, scope="class")
def setup(self, playwright: Playwright):
        global browser, context, page
        browser = playwright.chromium.launch(headless=False, channel="chrome", slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        url = ConfigManager.get_env_data()['web_url']
        page.goto(url)
        yield
        context.close()
        page.close()

@pytest.fixture(scope= "class")
def request_context(playwright: Playwright, request:FixtureRequest):
    request_context=playwright.request.new_context(base_url=CHUCK_BASE_URL)
    yield request_context
    request_context.dispose()


@pytest.fixture
def expense_flows(page):
    return WebWorkflows(page)


@pytest.fixture
def api_flows(request_context):
    return APIWorkflows(request_context)
