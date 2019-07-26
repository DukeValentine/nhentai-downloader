import shutil
import requests
import bs4
import os
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


def get_doujinshi_data (doujinshi_id,delay,retry):
    """
    Creates Doujinshi object for the given id and populates its fields from the API url_list(which is in JSON format)
    ID must be a string
    Check Doujinshi class to know more
    """
    try:
        if not doujinshi_id or not isinstance(doujinshi_id,str):
            raise TypeError('Bad id format') #ID received is not a string or is NULL
        
    except TypeError as error:
        logger.error('Bad id format')
        return None
        
        
    else:
        doujinshi = Doujinshi(doujinshi_id)
        
        info_regex = re.compile(r'\(\{.*\}\)')

        
        for attempt in range(1,retry+1):
            sleep(delay)
            response = requests.get("https://nhentai.net/g/{0}/".format(doujinshi_id),allow_redirects=True)
            
        
            if response.status_code is not constant.ok_code:
                logger.error("Error fetching doujinshi id[{0}]. Nhentai responded with {1} [Attempt {2} of {3}]" .format(doujinshi_id,response.status_code,attempt,retry+1))
                
                
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
            logger.error("Doujinshi id[{0}] not found after {1} attempts" .format(doujinshi_id,retry+1))
            logger.debug(response.text)
            print()
            logger.debug(requests.get("https://nhentai.net/g/{0}/".format(doujinshi_id)) )
            return None
            
        else:
            logger.info("Getting info from doujinshi id[{0}]".format(doujinshi_id))
            
            page_content = response.content
            page_html = bs4.BeautifulSoup(page_content, 'html.parser')
            doujinshi_info_text = ""
            
            for item in page_html.find_all("script"):
                
                if "gallery" in item.get_text():
                    #logger.debug(item)
                    doujinshi_info_text = item.get_text()
                
            doujinshi_info_json = info_regex.search(doujinshi_info_text).group().strip('(').strip(')')
            
            doujinshi.FillInfo(json.loads(doujinshi_info_json))
                    
            return doujinshi
            

def download_worker (path,overwrite,delay,retry,url):
    """
    Download file in given url in given path. Url must have the filename with extension (eg: https://i.nhentai.net/galleries/1343630/1.jpg)
    If Overwrite argument is false,the worker will check whether the file exists and skip if so
    """
    filename = url.split('/')[-1]
    
    filename = filename.split('\\')[-1] #deal with the case of the filename coming back as MEDIA_ID\*.jpg
    
    fullpath = os.path.join(path,filename)
    
    
    
    logger.debug("URL: {0}".format(url))
    logger.debug("Fullpath: {0}".format(fullpath))
    
    for attempt in range(1,retry+1):
        sleep(delay)
        req = requests.get(url, stream=True)
        
        if req.status_code == constant.ok_code:
            break
        else:
            sleep(delay)
        
    if req.status_code == constant.ok_code:
        if overwrite or not os.path.isfile(fullpath):
            logger.debug("Downloading {0}".format(filename))
            with open(fullpath, 'wb') as f:
                shutil.copyfileobj(req.raw, f)
                
        else:
            logger.debug("File {0} exists, overwriting disabled".format(filename))
    
    

def torrent_download_worker(path,session,delay,retry,id):
    url = "{0}{1}/download".format(constant.urls['GALLERY_URL'],id)
    fullpath = os.path.join(path, "{0}.torrent".format(id))
    
    logger.info("Downloading {0}.torrent".format(id))
    logger.debug(url)
    
    for attempt in range(1,retry+1):
        sleep(delay)
        logger.info("Attempt {0} for {1}.torrent".format(attempt,id))
        req = session.get(url, stream=True)
        logger.debug("Nhentai responded with {0} for {1}.torrent".format(req.status_code,id))
        
        if session.history:
            session.post(session.url)
        
        elif req.status_code == constant.ok_code:
            break
        else:
            sleep(delay)
        
    if req.status_code == constant.ok_code:
        with open(fullpath,"wb") as torrent_file:
            shutil.copyfileobj(req.raw, torrent_file)
        logger.debug("Download of {0}.torrent finished".format(id))
        
    else:
        logger.error("Failed to download torrent file")
        
def torrent_pool_manager(threads,path,delay,retry,id_list,session):
    downloaded_count = 0
    total_torrents = len(id_list)
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = {executor.submit(torrent_download_worker,path,session,delay,retry,id) : id for id in id_list}
        
        for item in completed_threads(results):
            downloaded_count +=1
            logger.info("Downloaded {0} of {1}".format(downloaded_count,total_torrents))


def image_pool_manager(threads,path,url_list,delay=0.4,retry=5,overwrite=True):
    """
    Create and manage a pool for downloading images
    Receives how many download threads there will be, along with the destination path and the url_list with all the images to download
    """
    
    downloaded_count = 0
    total_images = len(url_list)
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = {executor.submit(download_worker,path,overwrite,delay,retry,url) : url for url in url_list}
        for item in completed_threads(results):
            downloaded_count +=1
            logger.info("Downloaded {0} of {1}".format(downloaded_count,total_images))
    
    
def fetch_favorites(session,options):
    """
    Fetch doujinshi information from given page of the favorites of the given session.
    To download the found doujinshis, it is required to supply a true value to the download flag, otherwise it will only fetch their metadata
    Returns a list of fetched doujinshi
    Options must be a class with these attributes: tags,dir,threads,initial_page,last_page,verbose,download and overwrite
    """
    tags = options.tags
    directory = options.dir
    threads = options.threads
    page = options.initial_page
    max_page = options.last_page
    debug = options.verbose
    download = options.download
    overwrite = options.overwrite
    delay = options.delay
    retry = options.retry
    
    doujinshi_list = []
    
    
    search_string = '+'.join(tags)
    
    logger.debug(search_string)
    
    while (page <= max_page or not max_page):  #not max_page is for the default max_page value (max_page = 0), which means 'fetch until the last page of favorites
        logger.info("Getting page {0}".format(page))
        
        
        for attempt in range(1,retry+1):
            sleep(delay)
            response = session.get("{0}{1}&page={2}".format(constant.urls['FAV_URL'],search_string,page))
            
            if response.status_code is not constant.ok_code:
                logger.info("Nhentai responded with {0}".format(response.status_code))
                
            elif response.history:
                session.post(response.url)
        
        fav_page = session.get("{0}{1}&page={2}".format(constant.urls['FAV_URL'],search_string,page)).content
        fav_html = bs4.BeautifulSoup(fav_page, 'html.parser')
        fav_elem = fav_html.find_all('div' , class_ = 'gallery-favorite')
        
        page = page + 1
        
        if (not len(fav_elem)): #if there's no more favorite elements, it must mean the program passed the last page of favorites
            logger.info("No doujinshi found in page")
            break

        logger.info("{0} doujinshi found".format(len(fav_elem)) )
        
        id_list = []
        
        for id in fav_elem:
            id_list.append(id.get('data-id'))
        
        logger.debug("Id batch: {0}".format(id_list))
        doujinshi_list = doujinshi_list + fetch_id(options,id_list,session)
        logger.debug("Fetched {0} doujinshi so far".format(len(doujinshi_list)))
                
        
    return doujinshi_list

#tags,directory,threads = multiprocessing.cpu_count(),page = 1,max_page = 0 ,download=False,debug=False,overwrite=True
def search_doujinshi(options,session=None):
    """
    Using the given tags, search nhentai for doujinshi until max_page is reached.
    If the download argument is true, it will download found doujinshi in the given directory.
    Overwrite: whether it will overwrite already existing images
    """
    
    tags = options.tags
    directory = options.dir
    threads = options.threads
    page = options.initial_page
    max_page = options.last_page
    debug = options.verbose
    download = options.download
    overwrite = options.overwrite
    torrent = options.torrent
    delay = options.delay
    retry = options.retry
    
    
    
    #Nhentai joins search words with a '+' character
    search_string = '+'.join(tags)
    
    href_regex = re.compile(r'[\d]+') #Doujinshi in the search page have as the only identification the href in the cover, which is in the format /g/[id]. This regex filters only the id, thrasing out the rest of the link
    
    
    logger.debug("Base directory:{0}".format(directory))
    logger.debug("Page {0} to {1}".format(page,max_page))
        
    logger.info("Search tags: {0}".format(tags))
    
    doujinshi_list = []
    id_list = []
    
    while (page <= max_page or not max_page):
        logger.info("Getting doujinshi from {0}".format(constant.urls['SEARCH'] +  search_string) + "&page={0}".format(page))
        
        search_url = constant.urls['SEARCH'] +  search_string + "&page={0}".format(page)
        for attempt in range(1,retry+1):
            sleep(delay)
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
        
        
        sleep(delay)
        for id in search_elem:
            id_list.append(href_regex.search(id.get('href')).group())
            
            
        doujinshi_list = doujinshi_list + fetch_id(options,id_list)
        logger.debug("Fetched {0} doujinshi so far".format(len(doujinshi_list)))
            
        page = page + 1
        
        
        
    return doujinshi_list
    


def fetch_id(options,id,session=None):
    """
    Fetch doujinshi information from given ids.
    To download found doujinshi, the download flag must be given a true value. By default doujinshi are not downloaded
    """
    
    directory = options.dir
    threads = options.threads
    download = options.download
    debug = options.verbose
    overwrite = options.overwrite
    torrent = options.torrent
    delay = options.delay
    retry = options.retry
    cbz = options.cbz
    remove_after = options.remove_after
    
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
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = {executor.submit(get_doujinshi_data, id,delay,retry): id for id in id_list}
        
        for future in completed_threads(results):
            #if future.result() is not None:
            doujinshi_list.append(future.result())
    
    
    for id_doujinshi in doujinshi_list:
        if id_doujinshi is None:
            continue
        
        id_doujinshi.PrintDoujinshiInfo(verbose=True)
    
        if download:
            logger.info("Downloading doujinshi id[{0}]".format(id))
            
            url_list = id_doujinshi.generate_url_list()
            doujinshi_path = id_doujinshi.get_path(directory)
            logger.debug("Doujinshi path : {0}".format(doujinshi_path))
            
            io_utils.create_path(doujinshi_path)
            
            logger.debug("Starting image pool")
            logger.debug(url_list)
                
            image_pool_manager(threads,doujinshi_path,url_list,overwrite)
            if cbz:
                io_utils.create_cbz(directory,id_doujinshi.GetFormattedTitle(),remove_after)
            
            
    if torrent:
        if not (options.login and options.password):
            logger.warning("Login info not provided despite torrent argument being given, skipping .torrent download")
            return doujinshi_list
        
        elif not session:
            session = auth.login(options.login,options.password,options.verbose)
            
            if session is None:
                return doujinshi_list
        
        
        io_utils.create_path(options.dir)
        logger.debug("Starting torrent pool")
        torrent_pool_manager(threads,directory,delay,retry,id_list,session)
        logger.debug("End torrent pool")
            
        
            
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

            
    
    
