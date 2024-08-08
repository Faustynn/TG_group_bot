from database import setup_database
from utils import *
from config import *
from decorators import *
from handlers import *

if __name__ == "__main__":
    setup_database()
    bot.polling(none_stop=True)
