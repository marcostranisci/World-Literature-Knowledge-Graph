import requests,random,time
from requests.adapters import HTTPAdapter, Retry
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.service import Service


class SessionHandler:
    def __init__(self):
        self.static_session=self._static_session()
        self.dynamic_session=self._dynamic_session()
    
    def _static_session(self, retries=3, backoff=1):

        session = requests.Session()


        retries = Retry(total=retries, backoff_factor=backoff, status_forcelist=[ 502, 503, 504 ])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        return session

    def _dynamic_session(self, path='./geckodriver'):
        import os

        current_directory = os.getcwd()
        options = Options()
        options.add_argument("--headless")
        service = Service(executable_path=path)
        driver = webdriver.Firefox(service=service,options=options)
        driver.set_page_load_timeout(10)


        return driver
