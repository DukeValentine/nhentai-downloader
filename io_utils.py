import os
from logger import logger
from doujinshi import Doujinshi
import json

def write_idlist(directory,id_filename,id_list):
    logger.info("Writing id list output")
            
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
    
    logger.info("Writing json output")
    
    if debug:
        logger.debug("Filepath:{0}".format(os.path.join(directory,filename)))
            
    try:
        with open(os.path.join(directory,filename),"a+") as json_file:
            json_file.write(
                json.dumps(data, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4))
    
    except OSError as error:
        logger.error(repr(error))
        exit(1)
    
    else:
        logger.info("Writing finished")
    
    
    
    return 1

if __name__ == '__main__':
    test = Doujinshi("1225")
    test.title = "titlee"
    test.artist = "someone"
    test.pages = 25
    test.tags = ["tag1","tag2","tag3"]
    test.language = "english"
    
    
    #print (test.toJSON())
    
    directory = os.path.join(os.getcwd(),"json")
    path = os.path.join(directory,"test.json")
    print(path)
    #write_doujinshi_json(directory,"test.json",test)
    with open(path,"r") as file:
        data = json.load(file)
        
    
    for item in data:
        print ("{0}\n".format(item))
