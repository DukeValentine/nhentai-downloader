import os


urls = {
    'LOGIN_URL' : 'https://nhentai.net/login/',
    'FAV_URL' : 'https://nhentai.net/favorites/?q=',
    'API_URL' : 'https://nhentai.net/api/gallery/',
    'MEDIA_URL' : 'https://i.nhentai.net/galleries/',
    'SEARCH' : 'https://nhentai.net/search/?q=',
    'GALLERY_URL' : 'https://nhentai.net/g/'
}

INVALID_CHARACTERS = ['/', '\\', ':', '*', '?', '\"', '<', '>', '|']
CONTROL_CHARACTERS = ['\\t','\\n']
ok_code = 200

VERBOSE_LEVEL = 15


FILE_EXTENSION_LENGHT = 5
WINDOWS_MAX_PATH_LENGHT = 260 - FILE_EXTENSION_LENGHT
LINUX_MAX_FILENAME_LENGHT = 255 - FILE_EXTENSION_LENGHT

