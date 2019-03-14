import requests
from . import constant
import bs4
from .logger import logger

class LoginError(Exception):
    pass

def login(username, password,debug=False):
    
    nh_session = requests.Session()
    nh_session.headers.update({'Referer' : constant.urls['LOGIN_URL']} )
    
    login_page = nh_session.get(constant.urls['LOGIN_URL']).content
    login_html = bs4.BeautifulSoup(login_page, 'html.parser')
    
    csrf_token = login_html.find('input', attrs={"name":'csrfmiddlewaretoken'}).attrs['value']
    
    login_info = {
        'csrfmiddlewaretoken' : csrf_token,
        'username_or_email' : username,
        'password' : password
    
    }
    
    
    logger.debug("csrf token: {0}".format(login_info['csrfmiddlewaretoken']))
   
    try:
        response = nh_session.post(constant.urls['LOGIN_URL'], data=login_info)
        response_html = bs4.BeautifulSoup(response.text,'html.parser')

        logger.debug("Nhentai responded with {0}".format(response.status_code))
     
        if "Invalid username (or email) or password" in response.text:
            raise LoginError('Invalid username (or email) or password')
     
    except LoginError as error:
        logger.error(repr(error))
        return None
        
    else:
        logger.info("Logged in successfully")
        return nh_session
