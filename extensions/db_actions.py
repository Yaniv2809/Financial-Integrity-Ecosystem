import os
import sqlite3
import allure
from utils.logger import Logger

log = Logger()

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class DBActions:
    def __init__(self, data_base):
        self.data_base = data_base

    def close_db(self):
        self.data_base.close()

    @staticmethod
    def _get_db_type():
        """Reads DB type from env var (priority) or config.json fallback."""
        db_type = os.environ.get("DB_TYPE")
        if db_type:
            return db_type.lower()
        try:
            from config.config import ConfigManager
            config = ConfigManager.get_config()
            return config.get("db_type", "sqlite").lower()
        except Exception:
            return "sqlite"

    @staticmethod
    def _get_connection(db_path: str):
        """Returns a SQLite or MySQL connection based on db_type."""
        db_type = DBActions._get_db_type()

        if db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise ImportError("mysql-connector-python is not installed. Run: pip install mysql-connector-python")
            try:
                from config.config import ConfigManager
                mysql_cfg = ConfigManager.get_config().get("mysql", {})
            except Exception:
                mysql_cfg = {}

            return mysql.connector.connect(
                host=os.environ.get("MYSQL_HOST", mysql_cfg.get("host", "localhost")),
                port=int(os.environ.get("MYSQL_PORT", mysql_cfg.get("port", 3306))),
                user=os.environ.get("MYSQL_USER", mysql_cfg.get("user", "root")),
                password=os.environ.get("MYSQL_PASSWORD", mysql_cfg.get("password", "")),
                database=os.environ.get("MYSQL_DATABASE", mysql_cfg.get("database", "expense_test_db")),
            )
        else:
            return sqlite3.connect(db_path, timeout=10)

    @staticmethod
    def _adapt_query(query: str):
        """Convert SQLite-flavored SQL to MySQL-compatible SQL."""
        db_type = DBActions._get_db_type()
        if db_type != "mysql":
            return query

        # Skip PRAGMA statements (SQLite-only)
        if query.strip().upper().startswith("PRAGMA"):
            return None

        adapted = query
        # Replace ? placeholders with %s
        adapted = adapted.replace("?", "%s")
        # AUTOINCREMENT → AUTO_INCREMENT
        adapted = adapted.replace("AUTOINCREMENT", "AUTO_INCREMENT")

        return adapted

    @staticmethod
    @allure.step("Executing DB Query: {query}")
    def execute_query(db_path: str, query: str, params: tuple = ()) -> list:
        """
        Smart query executor that supports both SQLite and MySQL.
        Automatically adapts SQL syntax based on db_type configuration.
        """
        adapted_query = DBActions._adapt_query(query)
        if adapted_query is None:
            return []  # Skip PRAGMA commands for MySQL

        connection = None
        try:
            connection = DBActions._get_connection(db_path)
            cursor = connection.cursor()

            # SQLite-specific optimizations
            if DBActions._get_db_type() == "sqlite":
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA busy_timeout=10000;")

            cursor.execute(adapted_query, params)

            if adapted_query.strip().upper().startswith("SELECT"):
                records = cursor.fetchall()
                allure.attach(str(records), name="DB Results", attachment_type=allure.attachment_type.TEXT)
                return records
            else:
                connection.commit()
                return []

        except (sqlite3.Error, Exception) as error:
            log.error(f"DB Error: {error}")
            raise error

        finally:
            if connection:
                connection.close()
