# main/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from config import main_logging_level, telegram_logging_level

LOGGING_PATH = "../logs/log.log"

def setup_logging() -> None:
    """
    Sets up global logging
    """
    # get root logger
    rootLogger = logging.getLogger("")
    # create a rotating file handler with 1 backup file and 1 megabyte size
    fileHandler = RotatingFileHandler(LOGGING_PATH, "wa", 1_000_000, 1, "UTF-8")
    # create a default console handler
    consoleHandler = logging.StreamHandler()
    # create a formatting style (modified from hikari)
    formatter = logging.Formatter(
        fmt="%(levelname)-1.1s %(asctime)23.23s %(name)s @ %(lineno)d: %(message)s"
    )
    # add the formatter to both handlers
    consoleHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    # add both handlers to the root logger
    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleHandler)
    # set logging level whatever
    rootLogger.setLevel(main_logging_level)
    # it exposes the token in logs, add any other loggers that overwhelm the logs later
    logging.getLogger("urllib3.connectionpool").setLevel(telegram_logging_level)
    rootLogger.info("Set up logging!")