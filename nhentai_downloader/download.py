from . import constant
from .import io_utils
from .logger import logger

from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed as completed_threads
import requests
import shutil
from time import sleep
import os
from tqdm import tqdm 


def torrent_pool_manager(options,id_list,session):
    io_utils.create_path(options.directory)
    logger.debug("Starting torrent pool")
    
    downloaded_count = 0
    total_torrents = len(id_list)
    
    with ThreadPoolExecutor(max_workers=options.threads) as executor:
        results = {executor.submit(torrent_download_worker,options.directory,session,options.delay,options.retry,id) : id for id in id_list}
        
        for item in completed_threads(results):
            downloaded_count +=1
            logger.verbose("Downloaded {0} of {1}".format(downloaded_count,total_torrents))
            
    logger.debug("End torrent pool")


def image_pool_manager(options,doujinshi):
    """
    Create and manage a pool for downloading images
    Receives how many download threads there will be, along with the destination path and the url_list with all the images to download
    """
    
    logger.debug(doujinshi.page_ext)
    
    url_list = doujinshi.generate_url_list()
    doujinshi_path = doujinshi.get_path(options.directory)
    
    
    io_utils.create_path(doujinshi_path)
    
    
    logger.debug("Starting image pool")
    logger.debug(url_list)
    
    
    downloaded_count = 0
    total_images = len(url_list)
    
    with ThreadPoolExecutor(max_workers=options.threads) as executor:
        results = {executor.submit(download_worker,doujinshi_path,options.overwrite,options.delay,options.retry,url) : url for url in url_list}
        download_progress_bar = tqdm(total = total_images, desc = f"Downloading doujinshi id[{doujinshi.main_id}]", unit = "Image")
        
        for item in completed_threads(results):
            download_progress_bar.update(1)
            downloaded_count +=1
            logger.debug(f"Downloaded {downloaded_count} of {total_images}")
        
        download_progress_bar.close()
        logger.debug(f"Finished downloading doujinshi id[{doujinshi.main_id}]")


def download_worker (path,overwrite,delay,retry,url):
    """
    Download file in given url in given path. Url must have the filename with extension (eg: https://i.nhentai.net/galleries/1343630/1.jpg)
    If Overwrite argument is false,the worker will check whether the file exists and skip if so
    """
    
    filename = io_utils.get_filename_from_url(url)
    fullpath = io_utils.get_fullpath(path,filename)
    
    
    
    logger.debug(f"URL: {url}")
    logger.debug(f"Fullpath: {fullpath}")
    
    for attempt in range(1,retry+1):
        sleep(delay)
        req = requests.get(url, stream=True)
        
        if req.status_code == constant.ok_code:
            break
        else:
            sleep(delay)
        
    if req.status_code == constant.ok_code:
        if (overwrite == True or os.path.isfile(fullpath) == False):
            logger.debug(f"Downloading {filename}")
            with open(fullpath, 'wb') as f:
                shutil.copyfileobj(req.raw, f)
                
            return True
                
        else:
            logger.debug(f"File {filename} exists, overwriting disabled")
            return False
            
    
    

def torrent_download_worker(path,session,delay,retry,doujinshi_id):
    url = f"{constant.urls['GALLERY_URL']}{doujinshi_id}/download"
    fullpath = os.path.join(path, f"{doujinshi_id}.torrent")
    
    logger.info(f"Downloading {doujinshi_id}.torrent")
    logger.debug(url)
    
    for attempt in range(1,retry+1):
        sleep(delay)
        logger.info(f"Attempt {attempt} of {retry+1} for {doujinshi_id}.torrent")
        req = session.get(url, stream=True)
        logger.debug(f"Nhentai responded with {req.status_code} for {doujinshi_id}.torrent")
        
        if session.history:
            session.post(session.url)
        
        elif req.status_code == constant.ok_code:
            break
        else:
            sleep(delay)
        
    if req.status_code == constant.ok_code:
        with open(fullpath,"wb") as torrent_file:
            shutil.copyfileobj(req.raw, torrent_file)
        logger.debug(f"Download of {doujinshi_id}.torrent finished")
        
    else:
        logger.error("Failed to download torrent file")
