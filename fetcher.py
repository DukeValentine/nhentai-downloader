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
            
            doujinshi.main_id = doujinshi_id
            doujinshi.title = json_resp ['title']['english']
            doujinshi.media_id = json_resp['media_id']
            doujinshi.pages = json_resp['num_pages']
            
            if len(doujinshi.page_ext):
                del doujinshi.page_ext[:]
            
            if len(doujinshi.tags):
                del doujinshi.tags[:]
            
            for page in json_resp['images']['pages']:
                
                doujinshi.page_ext.append(doujinshi.ext[page['t']])
            
            
            for tag in json_resp['tags']:
                if tag['type'] == "tag":
                    doujinshi.tags.append(tag['name'])
                
                elif tag['type'] == "artist":
                    doujinshi.artist = tag['name']
                
                elif tag['type'] == "language" and tag['name'] != "translated":
                    doujinshi.language = tag['name']
                    
                elif tag['type'] == "group":
                    doujinshi.group = tag['name']
                    
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
        
        doujinshi_path = "{0}{1}".format(directory,fav_doujinshi.title.replace("/"," "))
        
        if debug:
            logger.debug("Doujinshi path : {0}\n".format(doujinshi_path))
            logger.debug("Title:{0}\nExt:{1}".format(fav_doujinshi.title,fav_doujinshi.page_ext))
        
        
        url_list = []
        
        try:
            os.makedirs(doujinshi_path,0o755)
            
        except OSError as error:
            if error.errno != errno.EEXIST:
                print(repr(error))
                raise
            else:
                logger.warning("Doujinshi folder already exists")
                
        
        if download:
            for index,ext in enumerate(fav_doujinshi.page_ext,1):
                url_list.append(constant.urls['MEDIA_URL'] + fav_doujinshi.media_id + "/{0}".format(index) + ext)
                
                
            
            image_pool = multiprocessing.Pool(threads)
            func = partial(download_worker,doujinshi_path)
            image_pool.map(func,url_list)
            image_pool.close()
            image_pool.join()
    
    return id_list

def fetch_id(id,directory,threads =None,download=False):
    """
    Fetch doujinshi information from given ids.
    To download found doujinshi, the download flag must be given a true value. By default doujinshi are not downloaded
    """
    
    for id_ in id:
        id_doujinshi = get_doujinshi_data(id)
        
        if download:
            url_list = []
            doujinshi_path = "{0}{1}".format(directory,id_doujinshi.title.replace("/"," "))
            
            for index,ext in enumerate(id_doujinshi.page_ext,1):
                url_list.append(constant.urls['MEDIA_URL'] + id_doujinshi.media_id + "/{0}".format(index) + ext)
            
            
            try:
                os.makedirs(doujinshi_path,0o755)
            
            except OSError as error:
                if error.errno != errno.EEXIST:
                    print(repr(error))
                    raise
            else:
                logger.warning("Doujinshi folder already exists")
                
            image_pool_manager(threads,doujinshi_path,url_list)
            
    
    
