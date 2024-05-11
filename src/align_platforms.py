import handler
import regex as re
from typing import AnyStr,Dict,List
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

    def scrape_books_from_goodreads(self,author_id: str) ->List[dict]:
        baseurl = 'https://www.goodreads.com/author/list/{}?page=1&per_page=10000'
        page = self.handler.dynamic_session(baseurl.format(author_id))
        source = page.page_source
        soup = BeautifulSoup(source)
        books = soup.find_all('tr',attrs={'itemtype':'http://schema.org/Book'})
        for book in books:
            d = dict()
            ratings = book.find('span',attrs={'class':'minirating'}).text
            if '0.00 avg rating' not in ratings:
                try:
                    title = book.find('a',attrs={'class':'bookTitle'})
                    d['book_title'] = re.sub('\n','',title.text)
                    d['book_id'] = title['href']
                    authors = book.find('span',attrs={'itemprop':'author'})
                    
                    authors = [{'name':x.find('a').text,'author_id':x.find('a')['href'].split('/')[-1].split('.')[0],'role':x.find('span',attrs={'class':'authorName greyText smallText role'})} for x in authors.find_all('div',attrs={'class':'authorName__container'})]
                    for item in authors:
                        if item['role'] is None:
                            item['role'] = 'not_specified'
                        else:
                            item['role'] = item['role'].text[1:-1]
                    d['authors'] = authors

                    
                    d['rating'] = re.search('[0-9]\.[0-9][0-9]',ratings.split('—')[0]).group()
                    d['ratingCount'] = re.search('[0-9]+',ratings.split('—')[1]).group()
                    print(d)
                except Exception as e: print(e)


