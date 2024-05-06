import requests,csv
import pandas as pd
import argparse,json,yaml,csv,traceback
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

parser = argparse.ArgumentParser()

parser.add_argument('-f','--filename')

args = parser.parse_args()

with open(args.filename) as f:
    vars = yaml.load(f, Loader=yaml.FullLoader)




fo = open(vars['files']['olid'],mode='a')

csv_writer = csv.DictWriter(fo,fieldnames=['entity','P648'])
#csv_writer.writeheader()



wikidata_ids = ''
wikipedia_ids = ''


class WikidataAuthors:
	
	def __init__(self):
		pass


	def find_wiki_titles(self,a_list,label:str='enwiki'):
		wikidata = 'https://www.wikidata.org/w/api.php'
		wd_params =  {'format':'json','action':'wbgetentities','ids':'{}'.format('|'.join(a_list)),'props':'sitelinks'}
		req = requests.get(wikidata,params=wd_params)
		labels = req.json()['entities']
		titles = list()
		for item in labels:
			if label:
				try:
					titles.append((item,label,labels[item]['sitelinks'][label]['title']))
				except Exception as e:print(e)
			else:
				for lang in labels[item]['sitelinks']:
					titles.append((item,lang,labels[item]['sitelinks'][lang]['title']))
			
		
		return titles

	def find_wiki_labels(self,a_list,label:str='en'):
		wikidata = 'https://www.wikidata.org/w/api.php'
		wd_params =  {'format':'json','action':'wbgetentities','ids':'{}'.format('|'.join(a_list)),'props':'labels'}
		req = requests.get(wikidata,params=wd_params)
		labels = req.json()['entities']
		titles = list()
		for item in labels:
			for lang in labels[item]['labels']:
				d = {'entity':item,'language':lang,'label':labels[item]['labels'][lang]['value']}
				titles.append(d)
			
		
		return titles

	def find_claim(self,a_list,claim:str,dtype='wikibase-item'):
		wikidata = 'https://www.wikidata.org/w/api.php'
		wd_params =  {'format':'json','action':'wbgetentities','ids':'{}'.format('|'.join(a_list)),'props':'claims','languages':'en'}
		req = requests.get(wikidata,params=wd_params)
		titles = list()
		if dtype == 'wikibase-item':
			for item in req.json()['entities']:
				try:
					titles.append({'entity':item,claim:req.json()['entities'][item]['claims'][claim][0]['mainsnak']['datavalue']['value']['id']})
				except Exception as e:continue
		elif dtype == 'external-id':
			for item in req.json()['entities']:
				try:
					titles.append({'entity':item,claim:req.json()['entities'][item]['claims'][claim][0]['mainsnak']['datavalue']['value']})
				except Exception as e:continue
		
		elif dtype == 'time':
			for item in req.json()['entities']:
				try:
					titles.append({'entity':item,claim:req.json()['entities'][item]['claims'][claim][0]['mainsnak']['datavalue']['value']['time']})
				except Exception as e:continue
			
		return titles
	
	def create_query(self,a_list,begin,end):
		
		query = begin
		occupations = list()
		for item in a_list:
			occupation = """{{?writer wdt:P106 wd:{0}}} UNION""".format(item)
			occupations.append(occupation)
			
		
		query+= " ".join(occupations).strip()
		query = query[:-6]
		query+= end

		return query
	
	def fetch_entities_from_wikidata(self,query):
		url = 'https://query.wikidata.org/sparql'
		params = {'format': 'json', 'query': query}
		req = requests.get(url, params=params)
		print(req)
		results = req.json()['results']['bindings']
		return results

'''



	
	

def find_wp_pages(a_string):
	wikipedia = 'https://en.wikipedia.org/w/api.php'
	
	wiki_params ={'action':'parse','page':'{}'.format(a_string),'format':'json'}

	req = requests.get(wikipedia,params=wiki_params)
	
	try:
		page = req.json()['parse']['text']
		return page
	except: 
		return None

def find_multiple_wp_pages(a_list):
	wikipedia = 'https://en.wikipedia.org/w/api.php'
	
	names = '|'.join([x[1] for x in a_list])
	mapping = {x[1]:x[0] for x in a_list}
	wiki_params = {'action':'query','prop':'revisions','titles':names,'format':'json','rvprop':'content'}
	
	req = requests.get(wikipedia,params=wiki_params)
	res = list()

	for item in req.json()['query']['pages']:
		
		try:
			d = dict()
			d['title'] = req.json()['query']['pages'][item]['title']
			d['wd_id'] = mapping[d['title']]
			d['txt'] = req.json()['query']['pages'][item]['revisions'][0]['*']
			res.append(d)
		except Exception as e:print(e)
	return res
	
'''


if __name__=='__main__':
	wiki = WikidataAuthors()
	'''l = ['Q155845']
	x = wiki.find_claim(l,'P648','external-id')
	print(x)'''
	'''query = wiki.create_query(a_list=vars['professions'],begin=vars['queries']['writers']['begin'],end=vars['queries']['writers']['end'])
	result = wiki.fetch_entities_from_wikidata(query)
	writers = list()
	for writer in result:
		writers.append({'entity':writer['writer']['value'],'P2963':writer['goodreads']['value']})
	
	df = pd.DataFrame(writers)
	df.entity = df.entity.apply(lambda x:x.split('/')[-1])
	df.P2963 = df.P2963.apply(lambda x:x.split('/')[-1])
	df.to_csv('../data/authorsGoodreads.csv',index=False)
	'''
	
	df = pd.read_csv(vars['files']['authors'])
	l = df.entity.to_list()

	chunks = [l[x:x+50] for x in range(0, len(l), 50)]

	for chunk in tqdm(chunks[1438:]):
		try:
			dobs = wiki.find_claim(chunk,'P648','external-id')
			csv_writer.writerows(dobs)
		except Exception as e:
			print(e)
			#traceback.print_exc()
			

