import shutil
import requests
import bs4
import os
import errno
import multiprocessing
from functools import partial
import re

from doujinshi import Doujinshi
import constant

import logging
from logger import logger
import io_utils
import json


def get_doujinshi_data (doujinshi_id):
    """
    Creates Doujinshi object for the given id and populates its fields from the API url_list
    ID must be a string
    """
    try:
        if not doujinshi_id or not isinstance(doujinshi_id,str):
            raise TypeError('Bad id format')
        
    except TypeError as error:
        logger.error('Bad id format')
        return None
        
        
    else:
        doujinshi = Doujinshi(doujinshi_id)
        
        try:
            resp = requests.get(constant.urls['API_URL'] + doujinshi.main_id)
            
            if resp.status_code is not 200:
                
                raise Exception("Couldn't get doujinshi id [%s]" % doujinshi_id)
            
        except Exception as error:
            logger.error("Doujinshi id[{0}] not found. Nhentai responded with {1}" .format(doujinshi_id,resp.status_code))
            
        else:
            logger.info("Getting info from doujinshi id[%s]" % doujinshi_id)
            
            json_resp = resp.json()
            
            doujinshi.fill_info(json_resp)
                    
            return doujinshi
            

def download_worker (path,overwrite,url):
    filename = url.split('/')[-1]
    fullpath = os.path.join(path,filename)
    
    req = requests.get(url, stream=True)
    
    
    if overwrite or not os.path.isfile(fullpath):
        logger.info("Downloading {0}".format(filename))
        with open(fullpath, 'wb') as f:
            shutil.copyfileobj(req.raw, f)
            
    else:
        logger.info("File {0} exists, overwriting disabled".format(filename))
    
    return fullpath

def image_pool_manager(threads,path,url_list,overwrite=True):
    """
    Create and manage a pool for downloading images
    """
    image_pool = multiprocessing.Pool(threads)
    func = partial(download_worker,path,overwrite)
    image_pool.map(func,url_list)
    image_pool.close()
    image_pool.join()
    
    
def fetch_favorites(page,session,directory,threads = multiprocessing.cpu_count(),download=False,debug=False,overwrite=True):
    """
    Fetch doujinshi information from given page of the favorites of the given session.
    To download the found doujinshis, it is required to supply a true value to the download flag. Default behaviour is to just return list of ids
    """
    logger.info("Getting page %d" % page)
                
    fav_page = session.get(constant.urls['FAV_URL'] + '?page=%d' % page).content
    

    fav_html = bs4.BeautifulSoup(fav_page, 'html.parser')

    fav_elem = fav_html.find_all('div' , class_ = 'gallery-favorite')
    
    

    logger.info("{0} doujinshi founnd".format(len(fav_elem)) )
    
    doujinshi_list = []
    
    for id in fav_elem:
        id = id.get('data-id')
        
        logger.info("Downloading doujinshi id[{0}]".format(id))
        
        if download:
            doujinshi_list = fetch_id(id,directory,threads,download,debug,overwrite)
            
    
    return doujinshi_list


def search_doujinshi(tags,directory,threads = multiprocessing.cpu_count(),max_page = 0 ,download=False,debug=False,overwrite=True):
    search_string = '+'.join(tags)
    
    page_num = 1
    
    href_regex = re.compile(r'[\d]+')
    
    if debug:
        logger.debug("Base directory:{0}".format(directory))
        
    logger.info("Search tags: {0}".format(tags))
    
    doujinshi_list = []
    
    while (page_num > max_page and max_page):
        logger.info("Getting doujinshi from {0}".format(constant.urls['SEARCH'] +  search_string) + "&page={0}".format(page_num))
        
        search_page = requests.get(constant.urls['SEARCH'] +  search_string + "&page={0}".format(page_num)).content
        search_html = bs4.BeautifulSoup(search_page,'html.parser')
        search_elem = search_html.find_all('a', class_ = 'cover')
        
        logger.info("Found {0} doujinshi in page".format(len(search_elem)))
        
        if (not len(search_elem)):
            break
        
        for id in search_elem:
            id = href_regex.search(id.get('href')).group()
            
            dlist = fetch_id(id,directory,threads,download,debug,overwrite)
            
            for elem in dlist:
                doujinshi_list.append(elem)
            
        page_num = page_num + 1
        
        
        
    return doujinshi_list
    
    

def create_doujinshi_path(doujinshi_path,permissions=0o755):
    try:
        os.makedirs(doujinshi_path,0o755)
            
    except OSError as error:
        if error.errno != errno.EEXIST:
            logger.error(repr(error))
            raise
        else:
            logger.warning("Folder already exists")

def fetch_id(id,directory,threads =None,download=False,debug=False,overwrite=True):
    """
    Fetch doujinshi information from given ids.
    To download found doujinshi, the download flag must be given a true value. By default doujinshi are not downloaded
    """
    doujinshi_list = []
    id_list = []
    
    if isinstance(id,str):
        id_list.append(id)
        
    else:
        id_list = id
    
    for id_ in id_list:
        id_doujinshi = get_doujinshi_data(id_)
        doujinshi_list.append(id_doujinshi)
        
        logger.info("Fetching doujinshi id[{0}]".format(id_))
        
        if download:
            url_list = id_doujinshi.generate_url_list()
            doujinshi_path = id_doujinshi.get_path(directory)
            
            if debug:
                logger.debug("Doujinshi path : {0}".format(doujinshi_path))
                logger.debug("Title:{0}".format(id_doujinshi.title))
                logger.debug("Pages:{0}".format(id_doujinshi.pages))
            
            create_doujinshi_path(doujinshi_path)
                
            image_pool_manager(threads,doujinshi_path,url_list,overwrite)
            
    return doujinshi_list
            
if __name__ == '__main__':
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    test_list = ["257565","257566","257525"]
    #dlist = fetch_id(test_list,os.path.join(os.getcwd(),'') + "id_test/",download=False,debug=True,overwrite=False)
    tags = ["impregnation","english","sword"]
    
    directory = os.path.join(os.getcwd(),"json")
    
    
    #print(dlist)
    dlist = search_doujinshi(tags,os.path.join(os.getcwd(),'') + 'search/',download=False,debug=True,max_page=1)
    
   
    io_utils.write_doujinshi_json(directory,"test.json",dlist)
            
    
    
