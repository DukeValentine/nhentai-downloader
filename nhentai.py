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


    parser = argparse.ArgumentParser (description = "Get a list of doujinshi from your favorites or tag searches \n Download galleries in image or cbz formats")

    auth = parser.add_argument_group('Authentication')
    debug = parser.add_argument_group('Debug')
    file_args = parser.add_argument_group('File options')
    search = parser.add_argument_group('Search options')
    download = parser.add_argument_group('Download options')


    file_args.add_argument ("--dir",'-D', action ="store", nargs='?', default=os.getcwd() + '/nhentai/',help ='Directory for saved files, defaults to ./nhentai/')
    file_args.add_argument ('-f', action="store", dest = "id_filename", default = 'ids.txt', help='Filename for the id list, ids.txt by default')

    auth.add_argument ('-l','--login', action="store", dest = "login", default = '')
    auth.add_argument ('-p','--password', action="store", dest = "password",default = '')

    debug.add_argument('-V','--verbose', action = "store_true", dest = "verbose", default = False, help = "Print aditional debug information") 

    search.add_argument ('--search', action = "store_true", default = False, help = "Sets whether it will get doujinshi from favorites or site-wide search")
    search.add_argument ('--id',default = '')
    search.add_argument ('-t','--tags' , action="store", dest = "tags", nargs='*',default=[], help ='Narrow doujinshi down by tags')
    search.add_argument ('--page', action = "store", type=int, dest = "initial_page", default = 1, help = "Initial page")
    search.add_argument ('--max-page', action = "store", type=int, dest = "last_page", default = 0, help = "Last page")


    download.add_argument('--download',action = "store_true", default = False, help = "Download found doujinshi")
    download.add_argument('--overwrite',action = "store_true",default = False, help ="Overwrite already downloaded images")





    login = parser.parse_args().login
    password = parser.parse_args().password
    id_filename = parser.parse_args().id_filename
    tag = parser.parse_args().tags
    directory = parser.parse_args().dir

    print (login)
    print (password)
    print (id_filename)
    print(tag)
    print(directory)

    print(parser.parse_args().search)
    print(parser.parse_args().download)

    print(parser.parse_args().initial_page)
    print(parser.parse_args().last_page)

    for item in tag:
        print (item)
    
    
    if not tag:
        print('no tags')


    image_queue = multiprocessing.Manager().Queue()


    nh_session = nhentai_login(login,password)

    if(nh_session is None):
        exit(1)
    #id_file = open(id_filename, "w")

    page_num = parser.parse_args().initial_page
    page_max = parser.parse_args().last_page
        
    while True:
        
        print("Getting page %d" % page_num)
                
        fav_page = nh_session.get(FAV_URL + '?page=%d' % page_num).content
        

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
                url_list.append(MEDIA_URL + fav_doujinshi.media_id + "/{0}".format(index) + ext)
                
                
            
            image_pool = multiprocessing.Pool(7)
            func = partial(download_worker,doujinshi_path)
            image_pool.map(func,url_list)
            image_pool.close()
            image_pool.join()
                #image_pool = multiprocessing.pool.Pool(7, download_worker, (image_queue,doujinshi_path,))
            
        
        page_num = page_num + 1
        if (not len(fav_elem)) or (page_num > page_max):
            break
        

        
        
    #id_file.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as error:
        print(repr(error))
        sys.exit(0)
