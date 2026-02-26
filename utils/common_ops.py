import csv
import json
import os

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
    


def read_data_from_csv(file_path):
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data