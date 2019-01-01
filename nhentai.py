import os
import requests
import bs4
import sys
import argparse
import multiprocessing
import queue
import time
import errno
import shutil
from functools import partial
import cli
from logger import logger
import fetcher
import auth
import constant


def main():
    options = cli.option_parser()


    login = options.login
    password = options.password
    id_filename = options.id_filename
    tag = options.tags
    directory = options.dir

    print (login)
    print (password)
    print (id_filename)
    print(tag)
    print(directory)

    print(options.search)
    print(options.download)

    print(options.initial_page)
    print(options.last_page)
    
    logger.info("Logging in...")
    nh_session = auth.login(login,password)

    if(nh_session is None):
        logger.error("Login failure,exiting")
        exit(1)
    #id_file = open(id_filename, "w")

    page_num = options.initial_page
    page_max = options.last_page
    
    
    if options.id:
        fetcher.fetch_id(options.id,options.dir,options.threads,options.download,options.verbose)
    
    elif options.search:
        fetcher.search_doujinshi(options.tags,options.dir,options.threads,options.last_page,options.download,options.verbose)
        
    else:
        while True:
            
            logger.info("Getting page %d" % page_num)
                    
            id_list = fetcher.fetch_favorites(page_num,nh_session,options.dir,options.threads,options.download,options.verbose)
            
            page_num = page_num + 1
            if (not len(id_list)) or (page_num > page_max):
                break
        

        
        
    #id_file.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as error:
        print(repr(error))
        sys.exit(0)
