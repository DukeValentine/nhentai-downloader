import shutil
import requests
import bs4
import os
import errno
import multiprocessing
from functools import partial

from doujinshi import Doujinshi
import constant
from logger import logger


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
            

    
    return None

def download_worker (path,url):
    filename = url.split('/')[-1]
    fullpath = path + '/' + filename
    
    logger.info("Downloading {0}".format(filename))
    #print(fullpath)
    
    req = requests.get(url, stream=True)
    
    with open(fullpath, 'wb') as f:
        shutil.copyfileobj(req.raw, f)
    
    return fullpath

def image_pool_manager(threads,path,url_list):
    image_pool = multiprocessing.Pool(threads)
    func = partial(download_worker,path)
    image_pool.map(func,url_list)
    image_pool.close()
    image_pool.join()
    
    
def fetch_favorites(page,session,directory,threads = multiprocessing.cpu_count(),download=False,debug=False):
    """
    Fetch doujinshi information from given page of the favorites of the given session.
    To download the found doujinshis, it is required to supply a true value to the download flag. Default behaviour is to just return list of ids
    """
    logger.info("Getting page %d" % page)
                
    fav_page = session.get(constant.urls['FAV_URL'] + '?page=%d' % page).content
    

    fav_html = bs4.BeautifulSoup(fav_page, 'html.parser')

    fav_elem = fav_html.find_all('div' , class_ = 'gallery-favorite')
    
    

    logger.info("{0} doujinshi founnd".format(len(fav_elem)) )
    
    id_list = []
    
    for id in fav_elem:
        id = id.get('data-id')
        
        logger.info("Downloading doujinshi id[{0}]".format(id))
                    
        id_list.append(id)
        
        fav_doujinshi = get_doujinshi_data(id)
        
        
        if download:
            doujinshi_path = fav_doujinshi.get_path(directory)
            
            url_list = fav_doujinshi.generate_url_list()
        
            if debug:
                logger.debug("Doujinshi path : {0}\n".format(doujinshi_path))
                logger.debug("Title:{0}".format(fav_doujinshi.title))
                logger.debug("Pages:{0}".format(fav_doujinshi.pages))
            
                
            create_doujinshi_path(doujinshi_path)
                
            image_pool_manager(threads,doujinshi_path,url_list)
    
    return id_list

def create_doujinshi_path(doujinshi_path,permissions=0o755):
    try:
        os.makedirs(doujinshi_path,0o755)
            
    except OSError as error:
        if error.errno != errno.EEXIST:
            print(repr(error))
            raise
        else:
            logger.warning("Doujinshi folder already exists")

def fetch_id(id,directory,threads =None,download=False,debug=False):
    """
    Fetch doujinshi information from given ids.
    To download found doujinshi, the download flag must be given a true value. By default doujinshi are not downloaded
    """
    id_list = []
    
    if isinstance(id,str):
        id_list.append(id)
        
    else:
        id_list = id
    
    for id_ in id_list:
        id_doujinshi = get_doujinshi_data(id_)
        
        logger.info("Downloading doujinshi id[{0}]".format(id_))
        
        if download:
            url_list = id_doujinshi.generate_url_list()
            doujinshi_path = id_doujinshi.get_path(directory)
            
            if debug:
                logger.debug("Doujinshi path : {0}\n".format(doujinshi_path))
                logger.debug("Title:{0}".format(id_doujinshi.title))
                logger.debug("Pages:{0}".format(id_doujinshi.pages))
            
            create_doujinshi_path(doujinshi_path)
                
            image_pool_manager(threads,doujinshi_path,url_list)
            
if __name__ == '__main__':
    
    test_list = ["257565","257566","257525"]
    fetch_id(test_list,os.path.join(os.getcwd(),'') + "id_test/",download=True,debug=True)
            
    
    
