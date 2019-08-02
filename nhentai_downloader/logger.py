import tqdm
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

VERBOSE_LEVEL = 15

logger = logging.getLogger('NHENTAI')

def verbose(self, message, *args, **kws):
    if self.isEnabledFor(VERBOSE_LEVEL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(VERBOSE_LEVEL, message, args, **kws)
        
        
class TqdmStream(object):
  @classmethod
  def write(_, msg):
    tqdm.tqdm.write(msg, end='')
        
class DummyTqdmFile(object):
    """ Dummy file-like that will write to tqdm
    https://github.com/tqdm/tqdm/issues/313
    """
    file = None

    def __init__(self, file):
        self.file = file

    def write(self, x):
        # Avoid print() second call (useless \n)
        if len(x.rstrip()) > 0:
            tqdm.tqdm.write(x, file=self.file, end='')

    def flush(self):
        return getattr(self.file, "flush", lambda: None)()

def logger_config(logging_level = logging.INFO):
    if not len(logger.handlers):
        logging.addLevelName(VERBOSE_LEVEL,"VERBOSE")
        logging.Logger.verbose = verbose
        
        logging.basicConfig(level=0,format = "[%(asctime)s][%(levelname)-8s]%(message)s" , datefmt = "%H:%M:%S", stream=TqdmStream)

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
