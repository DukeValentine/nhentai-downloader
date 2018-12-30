import requests
import constant
import bs4
from logger import logger

def login(username, password):
    
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
    
   # print(csrf_token)
   # print(login_info)
   
    try:
     response = nh_session.post(constant.urls['LOGIN_URL'], data=login_info)
     response_html = bs4.BeautifulSoup(response.text,'html.parser')
     
     if "Invalid username (or email) or password" in response.text:
         raise Exception('Login failure')
     
    except Exception as error:
        print(repr(error))
        return None
        
    else:
        logger.info("Logged in successfully")
        return nh_session
