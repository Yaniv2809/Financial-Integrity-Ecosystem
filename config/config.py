import json
import os

class ConfigManager:
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.json")

    @staticmethod
    def get_config():
        try:
            with open(ConfigManager.CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found at: {ConfigManager.CONFIG_FILE_PATH}")
        except json.JSONDecodeError:
            raise Exception("Error decoding JSON from the configuration file. Please check the JSON format.")

    @staticmethod
    def get_env_data():
        config = ConfigManager.get_config()
        active_env = config.get("active_env")

        return config.get("environments").get(active_env)