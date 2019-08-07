from tqdm import tqdm 

import shutil
import requests
import bs4
import os
import sys
import errno
import multiprocessing
import queue
from functools import partial
import re



import json
import logging
from time import sleep
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed as completed_threads


from .doujinshi import Doujinshi
from . import constant
from .logger import logger
from . import io_utils
from . import auth
from . import download


def get_doujinshi_data (doujinshi_id,delay,retry):
    """
    Creates Doujinshi object for the given id and populates its fields from the API url_list(which is in JSON format)
    ID must be a string
    Check Doujinshi class to know more
    """
    try:
        if doujinshi_id is None or not isinstance(doujinshi_id,str):
            raise TypeError('Bad id format')
        
    except TypeError as error:
        logger.error('Bad id format')
        return None
        
        
    else:
        doujinshi = Doujinshi(doujinshi_id)
        
        info_regex = re.compile(r'\(\{.*\}\)')

        
        for attempt in range(1,retry+1):
            sleep(delay)
            response = requests.get(f"https://nhentai.net/g/{doujinshi_id}/",allow_redirects=True)
            
        
            if response.status_code is not constant.ok_code:
                logger.error(f"Error fetching doujinshi id[{doujinshi_id}]. Nhentai responded with {response.status_code} [Attempt {attempt} of {retry+1}]")
                
                
            elif response.history:
                logger.debug("Redirect")
                logger.debug(response.content)
                
                response_html = bs4.BeautifulSoup(response, 'html.parser')
                csrf_token = response_html.find('input', attrs={"name":'csrfmiddlewaretoken'}).attrs['value']
                next = response_html.find('input',attrs={"name":"next"}).attrs['value']
    
                payload = {
                    'csrfmiddlewaretoken' : csrf_token,
                    'next' : next
                }
                
                logger.debug(requests.post(response.url,data=payload) )
                print()
            else:
                break
            
        if (response.status_code is not constant.ok_code) or response.history:
            logger.error(f"Doujinshi id[{doujinshi_id}] not found after {retry+1} attempts")
            logger.debug(response.text)
            print()
            logger.debug(requests.get(f"https://nhentai.net/g/{doujinshi_id}/"))
            return None
            
        else:
            logger.verbose(f"Getting info from doujinshi id[{doujinshi_id}]")
            
            page_content = response.content
            page_html = bs4.BeautifulSoup(page_content, 'html.parser')
            doujinshi_info_text = ""
            
            
            for item in page_html.find_all("script"):
                
                if "gallery" in item.get_text():
                    #logger.debug(item)
                    doujinshi_info_text = item.get_text()
                    
                    
            doujinshi_info_json = info_regex.search(doujinshi_info_text).group().strip('(').strip(')')

            
            doujinshi.FillInfo(json.loads(doujinshi_info_json.encode("UTF-8")))
                    
            return doujinshi
        
        

def batch_doujinshi_info_fetch(options,id_list):
    doujinshi_list = []
    
    with ThreadPoolExecutor(max_workers=options.threads) as executor:
        results = {executor.submit(get_doujinshi_data, id,options.delay,options.retry): id for id in id_list}
        info_bar = tqdm(total = len(id_list), desc = f"Fetching doujinshi info", unit = "Doujinshi")

        for future in completed_threads(results):
            info_bar.update(1)
            logger.debug(f"{future.result().main_id} has {len(future.result().page_ext)} images")
            doujinshi_list.append(future.result())
            
    return doujinshi_list


        
        
def remove_already_downloaded_cbz(path,url_list):
    return [url for url in url_list if io_utils.cbz_file_already_exists(path,url) == False]
    
        

        

    
def fetch_favorites(session,options):
    """
    Fetch doujinshi information from given page of the favorites of the given session.
    To download the found doujinshis, it is required to supply a true value to the download flag, otherwise it will only fetch their metadata
    Returns a list of fetched doujinshi
    Options must be a class with these attributes: tags,directory,threads,initial_page,maxg_page,verbose,download and overwrite
    """
 
    page = options.initial_page
    doujinshi_list = []
    
    
    search_string = '+'.join(options.tags)
    
    logger.debug(search_string)
    
    #not max_page is for the default max_page value (max_page = 0), which means 'fetch until the last page of favorites
    while (page <= options.max_page or not options.max_page):  
        logger.info(f"Getting page {page}")
        
        
        for attempt in range(1,options.retry+1):
           
            sleep(options.delay)
            
            
            current_page_url = f"{constant.urls['FAV_URL']}{search_string}&page={page}"
            response = session.get(current_page_url)
            
            if response.status_code == constant.ok_code:
                break
            
            elif response.status_code is not constant.ok_code:
                logger.error(f"Nhentai responded with {response.status_code}")
        
        fav_page = response.content
        fav_html = bs4.BeautifulSoup(fav_page, 'html.parser')
        fav_elem = fav_html.find_all('div' , class_ = 'gallery-favorite')
        
        page+=1
        
        if (not len(fav_elem)): #if there's no more favorite elements, it must mean the program passed the last page of favorites
            logger.info("No doujinshi found in page")
            break

        logger.info(f"{len(fav_elem)} doujinshi found")
        
        id_list = []
        
        for id in fav_elem:
            id_list.append(id.get('data-id'))
        
        doujinshi_list = doujinshi_list + fetch_id(options,id_list,session)
        logger.debug("Fetched {0} doujinshi so far".format(len(doujinshi_list)))
                
        
    return doujinshi_list


def search_doujinshi(options,session=None):
    """
    Using the given tags, search nhentai for doujinshi until max_page is reached.
    If the download argument is true, it will download found doujinshi in the given directory.
    Overwrite: whether it will overwrite already existing images
    """
    page = options.initial_page
    

    
    #Nhentai joins search words with a '+' character
    search_string = '+'.join(options.tags)
    
    href_regex = re.compile(r'[\d]+') #Doujinshi in the search page have as the only identification the href in the cover, which is in the format /g/[id]. This regex filters only the id, thrasing out the rest of the link
    
    
    logger.debug(f"Base directory:{options.directory}")
    logger.debug(f"Page {page} to {options.max_page}")
        
    logger.info(f"Search tags: {options.tags}")
    
    doujinshi_list = []
    id_list = []
    
    while (page <= options.max_page or not options.max_page):
        logger.info("Getting doujinshi from {0}".format(constant.urls['SEARCH'] +  search_string) + "&page={0}".format(page))
        
        search_url = constant.urls['SEARCH'] +  search_string + "&page={0}".format(page)
        for attempt in range(1,options.retry+1):
            sleep(options.delay)
            response = requests.get(search_url)
            
        
            if response.status_code is not constant.ok_code:
                logger.error("Error getting doujinshi from {0}".format(constant.urls['SEARCH'] +  search_string) + "&page={0}".format(page))
                
                
            elif response.history:
                logger.debug("Redirect")
                logger.debug(response.content)
                
                response_html = bs4.BeautifulSoup(response.content, 'html.parser')
                csrf_token = response_html.find('input', attrs={"name":'csrfmiddlewaretoken'}).attrs['value']
                next = response_html.find('input',attrs={"name":"next"}).attrs['value']
                url = "https://nhentai.net" + next
                payload = {
                    'csrfmiddlewaretoken' : csrf_token,
                    'next' : next
                }
                logger.debug(payload)
                logger.debug(response.url)
                logger.debug(requests.post(url,data=payload) )
                print()
            else:
                break
        
        search_page = response.content
        search_html = bs4.BeautifulSoup(search_page,'html.parser')
        search_elem = search_html.find_all('a', class_ = 'cover')
        
        logger.info("Found {0} doujinshi in page".format(len(search_elem)))
        
        if (not len(search_elem)): #if there's no more search elements, it must mean the program passed the last page of the search
            break
        
        
        sleep(options.delay)
        for id in search_elem:
            id_list.append(href_regex.search(id.get('href')).group())
            
            
        doujinshi_list = doujinshi_list + fetch_id(options,id_list)
        logger.info("Fetched {0} doujinshi so far".format(len(doujinshi_list)))
            
        page = page + 1
        
        
        
    return doujinshi_list
    


def fetch_id(options,id,session=None):
    """
    Fetch doujinshi information from given ids.
    To download found doujinshi, the download flag must be given a true value. By default doujinshi are not downloaded
    """

    doujinshi_list = []
    id_list = []
    
    #This snippet is to allow the function to work with both a single id and a list of ids
    if isinstance(id,str):
        id_list.append(id)
        
    else:
        id_list = id
        
    
    if not id_list:
        logger.critical("Fetch id: No ids were given")
        return doujinshi_list
    
    logger.verbose("Id batch: {0}".format(id_list))
    
    doujinshi_list = batch_doujinshi_info_fetch(options,id_list)
    
    
    doujinshi_counter = tqdm(total = len(doujinshi_list), desc = "Downloading doujinshi", unit = "Doujinshi")
    
    download_counter  = 0
    for id_doujinshi in doujinshi_list:
        download_counter+=1
        logger.debug(f"Fetching {download_counter} of {len(doujinshi_list)}")
        
        if id_doujinshi is None:
            continue
        
        id_doujinshi.PrintDoujinshiInfo(verbose=True)
    
        if options.download:
            logger.debug(f"Downloading doujinshi id[{id_doujinshi.main_id}]")
            
            if(options.cbz == True and options.overwrite == False and io_utils.cbz_file_already_exists(options.directory,id_doujinshi)):
                continue
        
            download.image_pool_manager(options,id_doujinshi)
            
            if options.cbz:
                io_utils.create_cbz(options.directory,id_doujinshi,options.remove_after)
        doujinshi_counter.update(1)
        
    doujinshi_counter.close()
            
    if options.torrent:
        if not (options.login and options.password):
            logger.critical("Login info not provided despite torrent argument being given, skipping .torrent download")
            return doujinshi_list
        
        elif not session:
            session = auth.login(options.login,options.password,options.verbose)
            
            if session is None:
                return doujinshi_list
        
        download.torrent_pool_manager(options,id_list,session)
            
        
            
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

            
    
    
