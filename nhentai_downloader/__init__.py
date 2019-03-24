__version__ = '0.5.1.0'
__author__ = 'DukeValentine' 
__email__ = 'humanix@posteo.de'


from .auth import login
from .logger import logger_config
from .cli import option_parser
from . import constant
from .doujinshi import Doujinshi
from . import fetcher
from . import io_utils

