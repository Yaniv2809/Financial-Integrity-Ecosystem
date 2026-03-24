import json
import os

class ConfigManager:
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.json")
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    
    @staticmethod
    def get_performance_config():
        config = ConfigManager.get_config()
        return config.get("performance")
    

    @staticmethod
    def get_db_path():
        config = ConfigManager.get_config()
        db_path = config.get("db_path")
        if not os.path.isabs(db_path):
            db_path = os.path.join(ConfigManager.PROJECT_ROOT, db_path)
        return db_path

    @staticmethod
    def get_db_2_path():
        config = ConfigManager.get_config()
        db_path = config.get("db_2_path")
        if not os.path.isabs(db_path):
            db_path = os.path.join(ConfigManager.PROJECT_ROOT, db_path)
        return db_path