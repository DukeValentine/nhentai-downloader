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
        self.compact_title = json_data['title']['pretty']
        self.media_id = json_data['media_id']
        self.pages = json_data['num_pages']
        self.num_favorites = json_data['num_favorites']
        self.upload_date = json_data['upload_date']
        
        if len(self.page_ext):
            del self.page_ext[:]
        
        if len(self.tags):
            for tag_type in self.tags:
                self.tags[tag_type].clear()
        
        for page in json_data['images']['pages']:
            
            self.page_ext.append(self.ext[page['t']])
        
        
        for data_tag in json_data['tags']:
            if (data_tag['name'] != 'translated'):
                self.tags[ data_tag['type'] ].append(data_tag['name'])
                
    def GetFormattedDate(self):
        return (datetime.utcfromtimestamp(self.upload_date).strftime('[%Y-%m-%d] (%a,%H:%M:%S)%Z') ) 
        
    def get_path(self,directory):
        title = ''
        
        if system() is "Windows":
            title = self.GetWindowsFormattedName(self.title)
            
        else:
            title = self.title.replace("/"," ")
        
        
        return os.path.join(directory, title)
    
    def GetFormattedTitle(self):
        if system() is "Windows":
            return( self.GetWindowsFormattedName(self.title))
            
        else:
            return(self.title.replace("/"," "))
        
    def GetWindowsFormattedName(self,name):
        formatted_title = name
        
        for character in constant.INVALID_CHARACTERS:
            formatted_title.replace(character,'')
            
        return formatted_title
    
    def generate_url_list(self):
        
        url_list = []
        
        for index,ext in enumerate(self.page_ext,1):
                filename = "{0}{1}".format(index,ext)
                #url_list.append(os.path.join(constant.urls['MEDIA_URL'],self.media_id,filename))
                url_list.append(constant.urls['MEDIA_URL'] + self.media_id + "/{0}".format(filename))
                
        return url_list
    
    def PrintDoujinshiInfo(self,verbose=False):
        logger.info("Title: {0}".format(self.title))
        logger.info("Language: {0}".format(', '.join(self.tags['language']) ))
        logger.info("Parody: {0}".format(', '.join(self.tags['parody']) ))
        logger.info("Artist: {0}".format(', '.join(self.tags['artist']) ))
        logger.info("Group: {0}".format(', '.join(self.tags['group']) ))
        logger.info("Total pages : {0}".format(self.pages))
        
        if verbose:
            logger.info("Characters : {0}".format(', '.join(self.tags['character']) ))
            logger.info("Tags : {0}".format(', '.join(self.tags['tag']) ))
            logger.info("Upload date: {0}".format(self.GetFormattedDate()) )
        
    
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
    


