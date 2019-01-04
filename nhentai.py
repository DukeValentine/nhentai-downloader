import os
import requests
import re
import bs4
import argparse
import time
import errno
import shutil
from functools import partial
import cli
from logger import logger
import fetcher
import auth
import constant
import logging
import io_utils


def main():
    options = cli.option_parser()
    
    id_regex = re.compile(r'[\d]+')


    login = options.login
    password = options.password
    #id_filename = options.id_filename
    tag = options.tags
    directory = options.dir
    
    #id_file = open(id_filename, "w")

    page_num = options.initial_page
    page_max = options.last_page
    
    input_id_list = []
    
    if options.input_filename:
        logger.info("Reading input file")
        input_path = os.path.join(options.dir,options.input_filename)
        
        try:
            with open(input_path,"r") as input_file:
                for line in input_file:
                    input_id_list.append(id_regex.search(line).group())
                    
        except OSError as error:
            logger.error(repr(error))
            exit(1)
            
        else:
            logger.info("{0} ids found in file".format(len(input_id_list)))
                
            
    
    
    if not options.verbose:
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    
    if not options.download:
        logger.info("Download argument not provided, found doujinshi will not be downloaded")
    
    
    if options.id:
        fetcher.fetch_id(options.id,options.dir,options.threads,options.download,options.verbose)
        
    
    elif options.search:
        if not options.tags:
            logger.warning("No search tags were given, the program will search the entirety of nhentai")
        
        dlist = fetcher.search_doujinshi(options.tags,options.dir,options.threads,options.last_page,options.download,options.verbose)
        
        if options.json:
            io_utils.write_doujinshi_json(options.dir,options.output_filename,dlist,options.verbose)
            
        else:
            id_list = (obj.main_id for obj in dlist)
            io_utils.write_idlist(options.dir,options.output_filename,id_list,options.verbose)
        
    else:
        if not login or not password:
            logger.error("Username or password not provided,exiting")
            exit(1)
        
        logger.info("Logging in...")
        nh_session = auth.login(login,password)

        if(nh_session is None):
            logger.error("Login failure,exiting")
            exit(1)
        
        doujinshi_list = []
        
        while (page_num > page_max):
            
            logger.info("Getting page %d" % page_num)
                    
            dlist = dlist + fetcher.fetch_favorites(page_num,nh_session,options.dir,options.threads,options.download,options.verbose)
            
            page_num = page_num + 1
            if (not len(dlist)):
                break
            
        if options.json:
            io_utils.write_doujinshi_json(options.dir,options.output_filename,dlist,options.verbose)
            
        else:
            id_list = (obj.main_id for obj in dlist)
            io_utils.write_idlist(options.dir,options.output_filename,id_list,options.verbose)    
        
        
        
    #id_file.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as error:
        print(repr(error))
        exit(1)
