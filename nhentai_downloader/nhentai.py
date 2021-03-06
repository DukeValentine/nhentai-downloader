import sys
from sys import exit
import os
from platform import system
import re
import argparse
import multiprocessing
import time
import errno
from nhentai_downloader import cli
from nhentai_downloader.logger import logger
from nhentai_downloader.logger import logger_config
from nhentai_downloader import fetcher
from nhentai_downloader import auth
from nhentai_downloader import constant
from nhentai_downloader import io_utils

import logging
import queue
import json

def main():

    options = cli.option_parser()
    logger_config(options.logging_level)


  
    
    logger_config()
    input_id_list = []
    
    
    

        
    
    
    
    if not options.download:
        logger.warning("Download argument not provided, found doujinshi will not be downloaded")
    
    
    if options.id or options.input_filename:
        ids = io_utils.read_input_file(options.directory,options.input_filename) + options.id
        dlist = fetcher.fetch_id(options,ids)
    
    
    elif options.search:
        if not options.tags:
            logger.warning("No search tags were given, the program will search the entirety of nhentai")
        
        dlist = fetcher.search_doujinshi(options)
        
    else:
        if not options.login or not options.password:
            logger.critical("Username or password not provided,exiting")
            exit(0)
        
        logger.info("Logging in...")
        nh_session = auth.login(options.login,options.password)

        if(nh_session is None):
            logger.critical("Login failure,exiting")
            exit(1)
        
        
        dlist = fetcher.fetch_favorites(nh_session,options)
        
    io_utils.write_output(options.directory,options.output_filename,dlist,options.json)
    
    logger.info("Finished")
        


if __name__ == '__main__':
    try:
        if system() is "Windows":
            multiprocessing.freeze_support()
        main()
    except KeyboardInterrupt as error:
        print(repr(error))
        exit(1)
