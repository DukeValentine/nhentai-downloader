import constant

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
        self.num_favorites = 0
        
    def fill_info(self, json_data):
        self.title = json_data ['title']['english']
        self.media_id = json_data['media_id']
        self.pages = json_data['num_pages']
        
        if len(self.page_ext):
            del self.page_ext[:]
        
        if len(self.tags):
            del self.tags[:]
        
        for page in json_data['images']['pages']:
            
            self.page_ext.append(self.ext[page['t']])
        
        
        for tag in json_data['tags']:
            if tag['type'] == "tag":
                self.tags.append(tag['name'])
            
            elif tag['type'] == "artist":
                self.artist = tag['name']
            
            elif tag['type'] == "language" and tag['name'] != "translated":
                self.language = tag['name']
                
            elif tag['type'] == "group":
                self.group = tag['name']
        
    def get_path(self,directory):
        return ("{0}{1}".format(directory,self.title.replace("/"," ")))
    
    def generate_url_list(self):
        
        url_list = []
        
        for index,ext in enumerate(self.page_ext,1):
                url_list.append(constant.urls['MEDIA_URL'] + self.media_id + "/{0}".format(index) + ext)
                
        return url_list
    
    
        
        
