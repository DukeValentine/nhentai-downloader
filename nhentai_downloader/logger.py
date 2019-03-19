import logging
import logging.handlers
import sys
from nhentai_downloader import constant
import os

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

logger = logging.getLogger('NHENTAI')

def logger_config():
    logging.basicConfig(level=0,format = "[%(asctime)s][%(levelname)-8s]%(message)s" , datefmt = "%H:%M:%S")

    log_dir = os.path.join(os.getcwd(),"log")

    if not os.path.exists( os.path.join(os.getcwd(),"log") ):
        os.makedirs(log_dir)
        

    log_path = os.path.join(log_dir,"nhentai.log")
    file_handle = logging.handlers.RotatingFileHandler(log_path,maxBytes = 10*1024*1024,backupCount = 10)



    format = logging.Formatter("[%(asctime)s][%(levelname)-8s]%(message)s" , datefmt = "%H:%M:%S")
    file_handle.setFormatter(format)
    logger.addHandler(file_handle)


    


if __name__ == '__main__':
    
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical error message')
