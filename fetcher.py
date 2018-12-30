import shutil
import requests
from doujinshi import Doujinshi
import constant
from constant import urls
import bs4
import os
import errno
import multiprocessing
from functools import partial

def get_doujinshi_data (doujinshi_id):
    try:
        if not doujinshi_id or not isinstance(doujinshi_id,str):
            raise Exception('Bad id format')
        
    except Exception as error:
        print(repr(error))
        return None
        
    else:
        doujinshi = Doujinshi(doujinshi_id)
        
        try:
            resp = requests.get(urls['API_URL'] + doujinshi.main_id)
            
            if resp.status_code is not 200:
                
                raise Exception("Couldn't get doujinshi id [%s]" % doujinshi_id)
            
        except Exception as error:
            print("Doujinshi id[{0}] not found. Nhentai responded with {1}" .format(doujinshi_id,resp.status_code))
            
        else:
            print("Getting info from doujinshi id[%s]" % doujinshi_id)
            
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
    print(fullpath)
    
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
    
    
def fetch_favorites(page,session,directory,threads = multiprocessing.cpu_count()):
    print("Getting page %d" % page)
                
    fav_page = session.get(urls['FAV_URL'] + '?page=%d' % page).content
    

    fav_html = bs4.BeautifulSoup(fav_page, 'html.parser')

    fav_elem = fav_html.find_all('div' , class_ = 'gallery-favorite')
    
    

    print("{0} doujinshi founnd".format(len(fav_elem)) )
    
    for id in fav_elem:
        id = id.get('data-id')
        print(id)
        fav_doujinshi = get_doujinshi_data(id)
        
        doujinshi_path = "{0}{1}".format(directory,fav_doujinshi.title)
        
        print(doujinshi_path)
        url_list = []
        
        try:
            os.makedirs("{0}{1}".format(directory,fav_doujinshi.title),0o755)
            
        except OSError as error:
            if error.errno != errno.EEXIST:
                print(repr(error))
                raise
            else:
                print("Doujinshi folder already exists")
        
        for index,ext in enumerate(fav_doujinshi.page_ext,1):
            url_list.append(urls['MEDIA_URL'] + fav_doujinshi.media_id + "/{0}".format(index) + ext)
            
            
        
        image_pool = multiprocessing.Pool(threads)
        func = partial(download_worker,doujinshi_path)
        image_pool.map(func,url_list)
        image_pool.close()
        image_pool.join()
    
    return len(fav_elem)

def fetch_id(id,directory):

    id_doujinshi = get_doujinshi_data(id)
    
    
