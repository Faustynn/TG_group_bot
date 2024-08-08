# main/logging_config.py
import logging

# Function to get the log level
def get_log_level(level_str):
    levels = {
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'critical': logging.CRITICAL
    }
    return levels.get(level_str.lower(), logging.INFO)


# Function to log messages to a file
def log_function(message, level_str, log_file, caller_file, line_number):
    level = get_log_level(level_str)
    logger = logging.getLogger(log_file)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    formatter = logging.Formatter(f'Time:%(asctime)s | Level:%(levelname)s | File:{caller_file} in {line_number} line | %(message)s',
    datefmt='%Y/%m/%d %H:%M')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    if level == logging.INFO:
        logger.info(message)
    elif level == logging.DEBUG:
        logger.debug(message)
    elif level == logging.ERROR:
        logger.error(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.CRITICAL:
        logger.critical(message)
    else:
        logger.info(message)
