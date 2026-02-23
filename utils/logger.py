import logging
import os
from datetime import datetime

class Logger:
    _instance = None  
    
    def __new__(cls): #create singleton instance
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self): #create logger folder and file
        self.logger = logging.getLogger("AutomationLogger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            log_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_directory, exist_ok=True)

            # create dinamic log file name based on current date and time
            log_filename = datetime.now().strftime("execution_%Y-%m-%d_%H-%M-%S.log")
            log_filepath = os.path.join(log_directory, log_filename)

            # מגדיר לאן הלוגים ילכו (לקובץ)
            file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
            
            # מגדיר גם הדפסה לקונסול (כדי שנראה בזמן אמת)
            console_handler = logging.StreamHandler()

            # פורמט ההודעה: תאריך ושעה - רמת ההודעה - ההודעה עצמה
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)


# from utils.logger import Logger
# log = Logger()
# log.info("Sending POST request to create an expense")