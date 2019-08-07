from . import constant
from datetime import datetime
from platform import system
import os
import json
from .logger import logger

class Doujinshi:
    ext = {
        'j' : '.jpg',
        'p' : '.png',
        'g' : '.gif'
    }
    
    def __init__(self,doujinshi_id,media_id = "",title = "",compact_title = "",pages=0,page_ext = [],num_favorites=0, upload_date=0):
        self.main_id = str(doujinshi_id)
        self.media_id = media_id
        self.title = title
        self.compact_title = compact_title
        self.tags = {
            'artist' : [],
            'group' : [],
            'character' : [],
            'language' : [],
            'tag' : [],
            'parody' : [],
            'category': []
            }
        self.pages = pages
        self.page_ext = page_ext
        self.num_favorites = num_favorites
        self.upload_date = upload_date
        
    def AddTags(self,new_tags,**kwargs):
        
        
        if isinstance(new_tags,str):
            self.tags.append(new_tags)
            
        else:    
            for tag in new_tags:
                self.tags.append(tag)
        
    def FillInfo(self, json_data):
        """
        Receives a dictionary containing all the information about the doujinshi
        """
        self.title = json_data ['title']['english']
        self.title = self.title.replace("\\t","")
        self.title = self.title.replace("&#039;","'")
        self.compact_title = json_data['title']['pretty'].replace("&#039;","'").replace("\\t","")
        self.media_id = json_data['media_id']
        self.pages = json_data['num_pages']
        self.num_favorites = json_data['num_favorites']
        self.upload_date = json_data['upload_date']
        self.page_ext = [self.ext[page['t']] for page in json_data['images']['pages']]
        
        for data_tag in json_data['tags']:
            if (data_tag['name'] != 'translated' and len(data_tag['name']) > 0):
                self.tags[ data_tag['type'] ].append(data_tag['name'])
                

    def format_tags(self,tag_type):
        return ",".join(self.tags[tag_type])
        
                
    def GetFormattedDate(self):
        return (datetime.utcfromtimestamp(self.upload_date).ctime() )
        
    def get_path(self,directory, extension = ""):
        title = self.GetFormattedTitle()
        
        if system() is "Windows":
            # MAX_PATH is 260 chars on windows (assuming program isn't run from an UNC path)
	
            if len(directory) + len(title) > constant.WINDOWS_MAX_PATH_LENGHT:
                title = title[:constant.WINDOWS_MAX_PATH_LENGHT - len(directory)]
            
        else:
            if(len(title) > constant.LINUX_MAX_FILENAME_LENGHT):
                title = title[:constant.LINUX_MAX_FILENAME_LENGHT]
            
            

        
        
        return os.path.join(directory, title + extension)
    
    def GetFormattedTitle(self):
        if system() is "Windows":
            return( self.GetWindowsFormattedName(self.title))
            
        else:
            return(self.title.replace("/"," "))
        
    def GetWindowsFormattedName(self,name):
        formatted_title = name
        
        for character in constant.INVALID_CHARACTERS:
            formatted_title = formatted_title.replace(character,'')
            
        return formatted_title
    
    def generate_url_list(self):
        
        url_list = []
        
        for index,ext in enumerate(self.page_ext,1):
                filename = f"{index}{ext}"
                #url_list.append(os.path.join(constant.urls['MEDIA_URL'],self.media_id,filename))
                url_list.append(f"{constant.urls['MEDIA_URL']}{self.media_id}/{filename}")
                
        return url_list
    
    def PrintDoujinshiInfo(self,verbose=False):
        logger.verbose(f"Media id : {self.media_id}")
        logger.info(f"Title: {self.title}")
        logger.verbose(f"Language: {self.format_tags('language')}")
        logger.verbose(f"Parody: {self.format_tags('parody')}")
        logger.verbose(f"Artist: {self.format_tags('artist')}")
        logger.verbose(f"Group: {self.format_tags('group')}")
        logger.verbose(f"Total pages : {self.pages}")
        
        logger.verbose(f"Characters: {self.format_tags('character')}")
        logger.verbose(f"Tags: {self.tags['tag']}")
        logger.verbose(f"Upload_date: {self.GetFormattedDate()}")
        logger.verbose(f"Total favorites : {self.num_favorites}")
        
    
    def toJSON(self):
        """
        Convert Doujinshi object to json format
        """
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    
class Tag_count:
    def __init__(self):
        self.tags = {}
        
    def Insert(self,tag):
        if tag in self.tags:
            self.tags[tag] = self.tags[tag] + 1
            
        else:
            self.tags[tag] = 1
    



