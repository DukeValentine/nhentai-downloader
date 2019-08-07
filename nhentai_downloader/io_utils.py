import os
from . import constant
from .logger import logger
from .doujinshi import Doujinshi
from .doujinshi import Tag_count
import json
import errno
import re
import shutil
from zipfile import ZipFile


def get_filename_from_url(url):
    filename = url.split('/')[-1]
    filename = filename.split('\\')[-1] #deal with the case of the filename coming back as MEDIA_ID\*.jpg
    return filename

def get_fullpath(path,filename):
    return os.path.join(path,filename)

def get_cbz_filename(directory):
    return directory + ".cbz"

def cbz_file_already_exists(path,directory):
    fullpath = os.path.join(path, f"{directory}.cbz")
    
    exists = os.path.isfile(fullpath)
    
    if(exists == True):
        logger.debug(f"{path} already exists")
    
    return  exists


def create_cbz(directory,doujinshi,remove_after=False):
    
    filepath = doujinshi.get_path(directory,".cbz")
    image_path = doujinshi.get_path(directory)
    
    try:
        with  ZipFile(filepath,"w") as cbz_doujinshi:
            logger.info("Writing:{0}".format(filepath))
            for image in os.listdir(image_path):
                cbz_doujinshi.write(os.path.join(image_path,image))
    
    except OSError as error:
        logger.error("Couldn't write file, system responded with {0}".format(repr(error)) )
        logger.error(f"{image_path} : {len(image_path)}")
        
    else:
        if remove_after:
            try:
                shutil.rmtree(image_path)
            
            except OSError as error:
                logger.error("Couldn't remove directory, system responded with {0}".format(repr(error)) )




def read_input_file(directory,filename):
    input_id_list = []
    id_regex = re.compile(r'[\d]+')
    
    if not filename:
        return input_id_list
    
    input_path = os.path.join(directory,filename)
    
    logger.info("Reading input file : {0}".format(input_path))
    
    try:
        with open(input_path,"r") as input_file:
            for line in input_file:
                input_id_list.append(id_regex.search(line).group())
                
    except OSError as error:
        logger.error(repr(error))
        return input_id_list
        
    else:
        logger.info("{0} ids found in file".format(len(input_id_list)))
        return input_id_list
    


def write_idlist(directory,id_filename,id_list):
    """
    Writes in a file a list of ids in the format https://nhentai.net/g/[id]/
    List of ids must contain ONLY the ids, otherwise the link syntax will be wrong
    """
    logger.info("Writing id list output")
    
    if not id_filename.endswith(".txt"):
        id_filename = id_filename + ".txt"
        
    filepath = os.path.join(directory,id_filename)
    
    
    logger.debug(f"Filepath:{filepath}")
            
    try:
        with open(filepath,"a+") as id_file:
            for doujinshi_id in id_list:
                id_file.write(f'{constant.urls["GALLERY_URL"]}{doujinshi_id}/\n')
    
    except OSError as error:
        logger.error(repr(error))
        exit(1)
    
    else:
        logger.info("Writing finished")
        
    
def write_doujinshi_json(directory,filename,data):
    """
    Converts a list of doujinshi to json format and writes it to a json file
    If destination directory does not exist, it will be created
    """
    logger.info("Writing json output")
    filepath = os.path.join(directory,filename)
    
    
    if not filename.endswith(".json"):
        filename = filename + ".json"
    
    logger.debug(f"Filepath:{filepath}")
    
    tags = Tag_count()
    
    for doujinshi in data:
        if doujinshi is None:
            continue
        
        for tag in doujinshi.tags:
            tags.Insert(tag)
            
    data.append(tags.tags)
    
    try:
        create_path(directory)
        
        with open(filepath,"w") as json_file:
            json_file.write(
                json.dumps(data, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4))
    
    except OSError as error:
        logger.error(repr(error))
        exit(1)
    
    else:
        logger.info("Writing finished")
        
def write_output(directory,filename,dlist,json,debug=False):
    if filename:
            if json:
                write_doujinshi_json(directory,filename,dlist)
                
            else:
                id_list = (obj.main_id for obj in dlist)
                write_idlist(directory,filename,id_list)
        
def create_path(path,permissions=0o755):
    """
    Creates given path with given permissions
    The user must have permissions to create subdirectories in the given directory
    """
    logger.debug(f"Doujinshi path : {path}")
    
    try:
        os.makedirs(path,0o755)
            
    except OSError as error:
        if error.errno != errno.EEXIST:
            logger.error(repr(error))
            raise
        else:
            logger.warning(f"Path {path} already exists")
            logger.debug(repr(error))

if __name__ == '__main__':
    test = Doujinshi("1225")
    test.title = "titlee"
    test.artist = "someone"
    test.pages = 25
    test.tags = ["tag1","tag2","tag3"]
    test.language = "english"
    
    directory = os.path.join(os.getcwd(),"json")
    path = os.path.join(directory,"test.json")
    print(path)
    #write_doujinshi_json(directory,"test.json",test)
    with open(path,"r") as file:
        data = json.load(file)
        
    
    for item in data:
        print ("{0}\n".format(item))
