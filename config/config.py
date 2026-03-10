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
    
    @staticmethod
    def get_performance_config():
        config = ConfigManager.get_config()
        return config.get("performance")
    

    @staticmethod
    def get_db_path():
        """מחשב באופן דינמי את הנתיב למסד הנתונים מכל מקום בפרויקט"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(project_root, "data", "expense_db.db")