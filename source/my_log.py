import logging
import sys
from logging.handlers import RotatingFileHandler


def get_console_handler():
    FORMATTER_INFO = logging.Formatter("%(message)s")    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER_INFO)
    console_handler.setLevel(logging.INFO)
    return console_handler


def get_file_handler(file_name):
    FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    file_handler = RotatingFileHandler(file_name, maxBytes=1024*100, backupCount=2)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, file_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG) # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(file_name))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
