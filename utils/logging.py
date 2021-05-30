import logging
import os
from time import gmtime


def create_logger(log_flag, request_id):

    if not os.path.exists('data/logs'):
        os.makedirs('data/logs')

    logging.Formatter.converter = gmtime
    logging.Formatter.default_time_format = '%Y-%m-%d %H:%M:%S %Z%z'
    log = logging.getLogger('Fanfiction Finder Bot')

    # create log directory for the request
    if log_flag:
        # adding file handler for logfile
        file_handler_format = '%(asctime)s | %(levelname)s | %(filename)s: L%(lineno)d: %(funcName)s: %(message)s'
        file_handler = logging.FileHandler(
            f'data/logs/{request_id}.log')
        file_handler.setFormatter(logging.Formatter(file_handler_format))
        log.addHandler(file_handler)
        log.setLevel(logging.INFO)

    else:
        # adding console handler
        console_handler = logging.StreamHandler()
        console_handler_format = '%(asctime)s | %(levelname)s | %(filename)s: L%(lineno)d: %(funcName)s: %(message)s'
        console_handler.setFormatter(logging.Formatter(console_handler_format))
        log.addHandler(console_handler)
        log.setLevel(logging.ERROR)

    return log
