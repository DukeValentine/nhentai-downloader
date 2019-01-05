import os
from .logger import logger
from .doujinshi import Doujinshi
import json
import errno




def write_idlist(directory,id_filename,id_list,debug=False):
    """
    Writes in a file a list of ids in the format https://nhentai.net/g/[id]/
    List of ids must contain ONLY the ids, otherwise the link syntax will be wrong
    """
    logger.info("Writing id list output")
    
    if not id_filename.endswith(".txt"):
        id_filename = id_filename + ".txt"
    
    if debug:
        logger.debug("Filepath:{0}".format(os.path.join(directory,id_filename)))
            
    try:
        with open(os.path.join(directory,id_filename),"a+") as id_file:
            for id in id_list:
                id_file.write("https://nhentai.net/g/{0}/\n".format(id))
    
    except OSError as error:
        logger.error(repr(error))
        exit(1)
    
    else:
        logger.info("Writing finished")
        
        
def write_doujinshi_json(directory,filename,data,debug=False):
    """
    Converts a list of doujinshi to json format and writes it to a json file
    If destination directory does not exist, it will be created
    """
    logger.info("Writing json output")
    
    if not filename.endswith(".json"):
        filename = filename + ".json"
    
    if debug:
        logger.debug("Filepath:{0}".format(os.path.join(directory,filename)))
            
    try:
        create_path(directory)
        
        with open(os.path.join(directory,filename),"w") as json_file:
            json_file.write(
                json.dumps(data, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4))
    
    except OSError as error:
        logger.error(repr(error))
        exit(1)
    
    else:
        logger.info("Writing finished")
        
def create_path(path,permissions=0o755):
    """
    Creates given path with given permissions
    The user must have permissions to create subdirectories in the given directory
    """
    try:
        os.makedirs(path,0o755)
            
    except OSError as error:
        if error.errno != errno.EEXIST:
            logger.error(repr(error))
            raise
        else:
            logger.warning("Folder already exists")

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
