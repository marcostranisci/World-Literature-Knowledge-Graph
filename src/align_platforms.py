import handler
from typing import AnyStr,Dict
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

class Aligner:
    
    def __init__(self) -> None:
        self.handler = handler.SessionHandler()

    def info_from_viaf(self,viaf_id:AnyStr) -> dict: 
        info = dict()
        baseurl = 'https://viaf.org/viaf/{}/viaf.json'

        page = self.handler.static_session.get(baseurl.format(viaf_id))
        info['author'] = viaf_id
        info['publishers'] = [(x['text'],x['sources']['sid']) if type(x['sources']['sid']) is str else \
                              (x['text'],','.join(x['sources']['sid'])) for x in page.json()['publishers']['data']]
        
        info['isbns'] = [x['text'] for x in page.json()['ISBNs']['data']]
        info['coauthors'] = [(x['text'],x['sources']['sid']) if type(x['sources']['sid']) is str else \
                              (x['text'],','.join(x['sources']['sid'])) for x in page.json()['coauthors']['data']]
        
        return info
    
    def find_goodread_author(self,isbn:str,author_name:str) -> dict:
        baseurl = 'https://www.goodreads.com/search?q={}'
        info = dict()
        page = self.handler.dynamic_session.get(baseurl.format(isbn))
        source = page.page_source
        soup = BeautifulSoup(source)
        links = soup.find_all('div',attrs={'ContributorLinksList'})
        authors = list()
        if len(links)>0:
            for link in links: 
                link = link.find('a')
                sim = SequenceMatcher(None,author_name,link.text)
                authors.append((author_name,link.text,link['href'],sim))
        info['authors'] = authors

        return info




