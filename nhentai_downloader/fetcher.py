import shutil
import requests
import bs4
import os
import errno
import multiprocessing
from functools import partial
import re
import logging


from .doujinshi import Doujinshi
from . import constant
from .logger import logger
from . import io_utils
from . import auth



def get_doujinshi_data (doujinshi_id):
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
        
        try:
            resp = requests.get(constant.urls['API_URL'] + doujinshi.main_id)
            
            if resp.status_code is not requests.codes.ok:
                raise Exception("Couldn't get doujinshi id [%s]" % doujinshi_id)
            
        except Exception as error:
            logger.error("Doujinshi id[{0}] not found. Nhentai responded with {1}" .format(doujinshi_id,resp.status_code))
            
        else:
            logger.info("Getting info from doujinshi id[{0}]".format(doujinshi_id))
            
            json_resp = resp.json()
            
            doujinshi.fill_info(json_resp)
                    
            return doujinshi
            

def download_worker (path,overwrite,url):
    """
    Download file in given url in given path
    If Overwrite argument is false,the worker will check whether the file exists and skip if so
    """
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
    Receives how many download threads there will be, along with the destination path and the url_list with all the images to download
    """
    
    #Since the path and overwrite arguments are common to all workers, they must be applied to all with a partial function because the map function only accepts one argument to apply to the target function
    image_pool = multiprocessing.Pool(threads)
    func = partial(download_worker,path,overwrite) 
    image_pool.map(func,url_list)
    image_pool.close()
    image_pool.join()
    
    
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
    
    doujinshi_list = []
    
    search_string = '+'.join(tags)
    
    logger.debug(search_string)
    
    while (page <= max_page or not max_page):  #not max_page is for the default max_page value (max_page = 0), which means 'fetch until the last page of favorites
        logger.info("Getting page {0}".format(page))
        
        fav_page = session.get("{0}{1}&page={2}".format(constant.urls['FAV_URL'],search_string,page)).content
        fav_html = bs4.BeautifulSoup(fav_page, 'html.parser')
        fav_elem = fav_html.find_all('div' , class_ = 'gallery-favorite')
        
        page = page + 1
        
        if (not len(fav_elem)): #if there's no more favorite elements, it must mean the program passed the last page of favorites
            break

        logger.info("{0} doujinshi founnd".format(len(fav_elem)) )
        
        
        
        for id in fav_elem:
            id = id.get('data-id')
        
            doujinshi_list = doujinshi_list + fetch_id(options,session)
                
        
    return doujinshi_list

#tags,directory,threads = multiprocessing.cpu_count(),page = 1,max_page = 0 ,download=False,debug=False,overwrite=True
def search_doujinshi(options):
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
    
    
    
    #Nhentai joins search words with a '+' character
    search_string = '+'.join(tags)
    
    href_regex = re.compile(r'[\d]+') #Doujinshi in the search page have as the only identification the href in the cover, which is in the format /g/[id]. This regex filters only the id, thrasing out the rest of the link
    
    
    logger.debug("Base directory:{0}".format(directory))
    logger.debug("Page {0} to {1}".format(page,max_page))
        
    logger.info("Search tags: {0}".format(tags))
    
    doujinshi_list = []
    
    while (page <= max_page or not max_page):
        logger.info("Getting doujinshi from {0}".format(constant.urls['SEARCH'] +  search_string) + "&page={0}".format(page))
        
        search_page = requests.get(constant.urls['SEARCH'] +  search_string + "&page={0}".format(page)).content
        search_html = bs4.BeautifulSoup(search_page,'html.parser')
        search_elem = search_html.find_all('a', class_ = 'cover')
        
        logger.info("Found {0} doujinshi in page".format(len(search_elem)))
        
        if (not len(search_elem)): #if there's no more search elements, it must mean the program passed the last page of the search
            break
        
        for id in search_elem:
            id = href_regex.search(id.get('href')).group()
            
            doujinshi_list = doujinshi_list + fetch_id(options)
            
        page = page + 1
        
        
        
    return doujinshi_list
    


def fetch_id(options,session=None):
    """
    Fetch doujinshi information from given ids.
    To download found doujinshi, the download flag must be given a true value. By default doujinshi are not downloaded
    """
    
    id = options.id
    directory = options.dir
    threads = options.threads
    download = options.download
    debug = options.verbose
    overwrite = options.overwrite
    torrent = options.torrent
    
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
    
    
    for id_ in id_list:
        logger.info("Fetching doujinshi id[{0}]".format(id_))
         
        id_doujinshi = get_doujinshi_data(id_)
        doujinshi_list.append(id_doujinshi)
        
        
        logger.debug("Title:{0}".format(id_doujinshi.title))
        logger.debug("Pages:{0}".format(id_doujinshi.pages))
    
        logger.debug("Fetched {0} doujinshi so far".format(len(doujinshi_list)))
        
       
        
        if download:
            logger.info("Downloading doujinshi id[{0}]".format(id))
            
            url_list = id_doujinshi.generate_url_list()
            doujinshi_path = id_doujinshi.get_path(directory)
            
            logger.debug("Doujinshi path : {0}".format(doujinshi_path))
            
            
            
            io_utils.create_path(doujinshi_path)
                
            image_pool_manager(threads,doujinshi_path,url_list,overwrite)
            
            
        if torrent:
            if not (options.login and options.password):
                logger.warning("Login info not provided despite torrent argument being given, skipping .torrent download")
                break
            
            elif not session:
                session = auth.login(options.login,options.password,options.verbose)
                
                if session is None:
                    break
                
            
            path = os.path.join(options.dir,"{0}.torrent".format(id_doujinshi.main_id))
            url = "{0}{1}/download".format(constant.urls['GALLERY_URL'],id_doujinshi.main_id)
            logger.debug("Path: {0}\nUrl:{1}".format(path,url))
            
            
            io_utils.create_path(options.dir)
            
            
            
            req = session.get(url, stream=True)
            with open(path,"wb") as torrent_file:
                shutil.copyfileobj(req.raw, torrent_file)
            
        
            
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

            
    
    
