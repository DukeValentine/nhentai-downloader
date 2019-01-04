import logging
import sys

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


logger = logging.getLogger('[NHENTAI]')
logging.basicConfig(level=0,format = "\r[%(asctime)s][%(levelname)-8s]   %(message)s" , datefmt = "%H:%M:%S")


if __name__ == '__main__':
    
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical error message')
