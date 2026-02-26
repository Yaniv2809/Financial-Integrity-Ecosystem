from playwright.sync_api import Browser, Playwright
from utils.common_ops import load_config
CONFIG = load_config()

def get_browser(playwright: Playwright,browser_type)->Browser:

    launch_args = ["--start-maximized"]
    if browser_type == "chrome":
        return playwright.chromium.launch(headless=CONFIG["HEADLESS"], channel="chrome", slow_mo=CONFIG["SLOW_MO"], args=launch_args)
    elif browser_type == "edge":
        return playwright.chromium.launch(headless=CONFIG["HEADLESS"], channel="msedge", slow_mo=CONFIG["SLOW_MO"], args=launch_args)
    else:
        raise Exception("Unsupported Browser was provided!")