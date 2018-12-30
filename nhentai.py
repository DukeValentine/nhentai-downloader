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


LOGIN_URL = 'https://nhentai.net/login/'
FAV_URL = 'https://nhentai.net/favorites/'
API_URL='https://nhentai.net/api/gallery/'
MEDIA_URL='https://i.nhentai.net/galleries/'


class Doujinshi:
    
    ext = {
        'j' : '.jpg',
        'p' : '.png'
    }
    
    def __init__(self,doujinshi_id):
        self.main_id = str(doujinshi_id)
        self.media_id = ''
        self.title = ''
        self.artist = ''
        self.group = ''
        self.language = ''
        self.tags = []
        self.pages = 0
        self.page_ext = []
        

def nhentai_login(username, password):
   # print('username:' + username + ', ' + 'password:' + password)
    
    nh_session = requests.Session()
    nh_session.headers.update({'Referer' : LOGIN_URL} )
    
    login_page = nh_session.get(LOGIN_URL).content
    login_html = bs4.BeautifulSoup(login_page, 'html.parser')
    
    csrf_token = login_html.find('input', attrs={"name":'csrfmiddlewaretoken'}).attrs['value']
    
    login_info = {
        'csrfmiddlewaretoken' : csrf_token,
        'username_or_email' : username,
        'password' : password
    
    }
    
   # print(csrf_token)
   # print(login_info)
   
    try:
     response = nh_session.post(LOGIN_URL, data=login_info)
     response_html = bs4.BeautifulSoup(response.text,'html.parser')
     
     if "Invalid username (or email) or password" in response.text:
         raise Exception('Login failure')
     
    except Exception as error:
        print(repr(error))
        return None
        
    else:
        print("Logged in successfully")
        return nh_session


def get_doujinshi_data (doujinshi_id):
    
    try:
        if not doujinshi_id or not isinstance(doujinshi_id,str):
            raise Exception('Bad id format')
        
    except Exception as error:
        print(repr(error))
        
    else:
    
        doujinshi = Doujinshi(doujinshi_id)
        
        try:
            resp = requests.get(API_URL + doujinshi.main_id)
            
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

    for item in tag:
        print (item)
    
    
    if not tag:
        print('no tags')
        
    

    image_queue = multiprocessing.Manager().Queue()


    logger.info("Logging in...")
    nh_session = auth.login(login,password)

    if(nh_session is None):
        exit(1)
    #id_file = open(id_filename, "w")

    page_num = options.initial_page
    page_max = options.last_page
        
    while True:
        
        logger.info("Getting page %d" % page_num)
                
        id_list = fetcher.fetch_favorites(page_num,nh_session,options.dir,7,options.download,options.verbose)
        
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
