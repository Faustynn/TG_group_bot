from database import setup_database
from utils import *
from config import *
from decorators import *
from handlers import *
from logging_config import *

if __name__ == "__main__":
    setup_database()
    log_function("Start main", config["log_levels"]["level1"],config["log_files"]["commands"], "main.py", 10)
    bot.polling(none_stop=True)
