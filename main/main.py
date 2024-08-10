from database import setup_database
from utils import *
from config import *
from decorators import *
from handlers import *
from logging_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    setup_database()
    logger.info("Starting bot!")
    bot.polling(none_stop=True)