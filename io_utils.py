import os
from logger import logger

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
        
        
def write_doujinshi_json(directory,filename,doujinshi):
    
    
    
    return 1
    
