import json
import os


class ConfigManager:
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.json")
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def get_config():
        try:
            with open(ConfigManager.CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
                config = json.load(file)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found at: {ConfigManager.CONFIG_FILE_PATH}")
        except json.JSONDecodeError:
            raise Exception("Error decoding JSON from the configuration file. Please check the JSON format.")

        config["db_type"] = os.environ.get("DB_TYPE", config.get("db_type", "sqlite"))
        config["headless"] = os.environ.get("HEADLESS", str(config.get("headless", False))).lower() == "true"
        return config

    @staticmethod
    def get_env_data():
        config = ConfigManager.get_config()
        active_env = config.get("active_env")
        env_data = config.get("environments", {}).get(active_env, {})

        env_data["web_url"] = os.environ.get("WEB_URL", env_data.get("web_url"))
        env_data["api_url"] = os.environ.get("API_URL", env_data.get("api_url"))
        env_data["flask_api_url"] = os.environ.get("FLASK_API_URL", env_data.get("flask_api_url"))
        env_data["ai_url"] = os.environ.get("AI_URL", env_data.get("ai_url"))
        env_data["currency_api_url"] = os.environ.get("CURRENCY_API_URL", env_data.get("currency_api_url"))

        return env_data

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
