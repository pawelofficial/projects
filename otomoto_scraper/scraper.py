import requests
from bs4 import BeautifulSoup
import pandas as pd 
from tabulate import tabulate
import numpy as np 
from pandas.plotting import parallel_coordinates
import re 
import json
import logging 
import httpx 
import asyncio 
import datetime
import time 
logging.basicConfig(level=logging.INFO,filemode='w',filename='./logs/scraper.log',format='%(asctime)s - %(levelname)s - %(message)s')


OFFERS_LIST='https://www.otomoto.pl/osobowe/renault/clio/od-2015?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=filter_float_price%3Adesc&search%5Badvanced_search_expanded%5D=true'
OFFERS_LIST='https://www.otomoto.pl/osobowe/mini?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Ato%5D=40000'
OFFER_DETAILS_URL='https://www.otomoto.pl/osobowe/oferta/renault-clio-szukasz-idealu-zapraszam-nawi-tempomat-podgrzewane-fotele-ID6FRmcm.html'

# cleans up list of lists if it has two items 
def clean_offer_details(offer_details):
    get_numbers = lambda x: ''.join(re.findall(r'\d+', x.replace(' ', '')))
    get_numbers_keys=['ROK PRODUKCJI','PRZEBIEG','MOC','POJEMNOŚĆ SKOKOWA','CENA']
    fun_dict={'ROK PRODUKCJI': get_numbers_keys
              ,'PRZEBIEG': get_numbers_keys
              ,'MOC': get_numbers_keys
              ,'POJEMNOŚĆ SKOKOWA': get_numbers_keys
              ,'CENA': get_numbers_keys
              } 
    clean_offer_details=[]
    for l in offer_details:
        if len(l)!=2:
            continue
        key=l[0]
        val=l[1]
        if key.upper().strip() in list(fun_dict.keys()): #  get_numbers_keys : 
            f=fun_dict[key.upper().strip()]
            val=get_numbers(val)
            
        clean_offer_details.append([key.strip(),val.strip()])
    return clean_offer_details

# request get to soup 
def get_soup(url,use_backup=False):
    if not use_backup:
        response = requests.get(url,timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
    # dump soup 
    else:
        with open('./data/soup.html','r',encoding="utf-8") as f:
            soup=f.read()
            soup=BeautifulSoup(soup, 'html.parser')
    
    with open('./data/soup.html','w',encoding="utf-8") as f:
        f.write(str(soup))
    return soup, response.status_code


async def fetch(url):
    headers= {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url,headers=headers)
        return response

async def fetch_all(urls, delay_interval=50, delay_seconds=1):
    tasks = []
    for i, url in enumerate(urls):
        tasks.append(fetch(url))
        # Introduce a delay every `delay_interval` requests
        if (i + 1) % delay_interval == 0:
            await asyncio.sleep(delay_seconds)
    responses = await asyncio.gather(*tasks)
    return responses

def parallel_fetch(urls):
    return asyncio.run(fetch_all(urls))

def get_soups_nicely(urls_list,sleep_time=1,max_retries=5): # returns soups and makes sure statuses are 200 ! 
    pages_d={url:{'soup':None,'status':None}for url in urls_list}
    no_of_tries=0
    while not all([v['status']==200 for k,v in pages_d.items()]) and no_of_tries<max_retries: # yeah yeah this is not very efficient i know bro 
        # print stztuses
        print(f'not 200 statuses: {len([k for k,v in pages_d.items() if v["status"]!=200])}')
        for k,v in pages_d.items():
            if v['status']!=200:
                soup,status=get_soup(k)
                pages_d[k]={'soup':soup,'status':status}
        no_of_tries+=1
        time.sleep(sleep_time)
    return pages_d,set([v['status'] for k,v in pages_d.items()])

def parallel_fetch_nicely(urls,max_retries=10,sleep_time=0.1):
    fetch_d={url:{'status':None,'soup':None} for url in urls}
    check_statuses=lambda d: all([v['status']==200 for k,v in d.items()])                    # checks if all statuses are 200
    make_fetch_d =  lambda responses: {r.url: {'status':r.status_code, 'soup': BeautifulSoup(r.text, 'html.parser')  } for r in responses} # parallel fetch into a d from a list 
    ## get urls of fetch_d where status is not 200 
    get_urls_not_200 =  lambda d: [k for k,v in d.items() if v['status']!=200]                 # get urls of fetch_d where status is not 200    
    #parallel_fetch_nicely
    
    fetch_d=make_fetch_d(parallel_fetch(urls))
    no=0
    while not check_statuses(fetch_d) and no<=max_retries:
        bad_urls=get_urls_not_200(fetch_d)
        fetch_d.update(make_fetch_d(parallel_fetch(bad_urls)))
        logging.info(f'not 200 statuses: {len(bad_urls)}')
        time.sleep(sleep_time)
        no+=1
    
    return fetch_d,set([v['status'] for k,v in fetch_d.items()])
    



        
def main_parallel(OFFERS_LIST):
    soup=get_soup(OFFERS_LIST)                              # 1. get soup
    pages_urls=get_no_of_pages(get_soup(OFFERS_LIST)  )     # 2. get all pages
    all_offer_links=[]
    for pu in pages_urls:
        offers_links=get_links_from_site(get_soup(pu))
        all_offer_links+=offers_links
    
    all_offer_responses=parallel_fetch(all_offer_links)
    all_offer_statuses={r.url: r.status_code for r in all_offer_responses}
    print(all_offer_statuses) # all 403 
    # print how many not 200 statuses 
    print(f'not 200 statuses: {len([k for k,v in all_offer_statuses.items() if v!=200])}')
    return all_offer_statuses
    


# scrapes links with a keyword from a website 
def get_links_from_site(soup,keyword='osobowe/oferta') -> list:
    links = []
    for link in soup.find_all('a', href=True):
        if keyword in link['href']:
            full_link = f"{link['href']}"        
            if full_link not in links:    # dont add duplicates
                links.append(full_link)
    return links


      

# scraping the data 
def get_tag_contents(soup, tag='div', attrs={'data-testid': 'advert-details-list'}, sub_tags=['p']) -> list:
    contents = []
    div_element = soup.find(tag, attrs)

    
    if div_element is None:
        print('element not found')
        logging.warning(f'element not found {tag} {attrs}')
        return None, None
    div_text=div_element.get_text(strip=True)
    # Define a function to filter tags based on the sub_tags list
    def filter_func(tag):
        return tag.name in sub_tags
    
    for element in div_element.find_all(filter_func):
        d = {element.name: element.get_text(strip=True)}
        contents.append(d)
    output_list=[]
    
    # range with step based on sub_tags len     
    for n in range(0,len(contents),len(sub_tags)):
        l=contents[n:n+len(sub_tags)]
        vals=[v for d in l for k,v in d.items()]
        output_list.append(vals)
        
    return output_list,div_text

    # cleans up list of list if it has two items

# scraping the data
def get_data_from_offer(soup) -> list:


    offer_data={}
    # find offer details  
    class_='advert-details-list'
    offer_details,_=get_tag_contents(soup
                    ,tag='div'
                    ,attrs={'data-testid': class_}
                    ,sub_tags=['p','a'])
    offer_details=clean_offer_details(offer_details)
    offer_data['offer_details']=offer_details
    
    class_='ooa-ho1qnd esicnpr7'
    price,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['h3']
                           )
    price=price[0][0].replace(' ','').replace('PLN','')
    offer_data['cena']=price
    # find description 
    class_='ooa-1xkwsck e1ku3rhr0'
    _,desc=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['div']
                           )
    offer_data['description']=desc
    # find wyposazenie 
    class_='ooa-0 evccnj12'
    wypo,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['p']
                           )
    offer_data['wyposazenie']=wypo
    # informacje o delaerze
    class_='ooa-yd8sa2 e6p1fgn3'
    data,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['p']
                           )
    offer_data['dealer']=data

    # lokalizacja 
    class_='ooa-yd8sa2 es06uqf0'
    data,txt=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['a']
                           )

    result = re.sub(r'\..+?\}', '', data[0][0] )
    offer_data['loc']=result

    # title
    class_='offer-title big-text e1aiyq9b1 ooa-ebtemw er34gjf0'
    data,txt=get_tag_contents(soup
                           ,tag='h3'
                           ,attrs={'class': class_}
                           ,sub_tags=['a']
                           )
    title=txt
    offer_data['tytul']=title
    
    
    
    return offer_data
    
    
def get_no_of_pages(soup):
    class_='ooa-1oll9pn er8sc6m7'
    data,txt=get_tag_contents(soup
                    ,tag='div'
                    ,attrs={'class': class_}
                    ,sub_tags=['li'])
    max_page=max([int(d[0]) for d in data if d[0].isdigit()])
    
    meta_tag = soup.find('meta', {'property': 'og:url'})
    link = meta_tag['content'] if meta_tag else None

    all_links=[link]
    for no in range(2,max_page+1):
        all_links.append(link+f'&page={no}')
    
    return all_links
    

def get_soups_nicely(urls_list,sleep_time=1,max_retries=5): # returns soups and makes sure statuses are 200 ! 
    pages_d={url:{'soup':None,'status':None}for url in urls_list}
    no_of_tries=0
    while not all([v['status']==200 for k,v in pages_d.items()]) and no_of_tries<max_retries: # yeah yeah this is not very efficient i know bro 
        # print stztuses
        print(f'not 200 statuses: {len([k for k,v in pages_d.items() if v["status"]!=200])}')
        for k,v in pages_d.items():
            if v['status']!=200:
                soup,status=get_soup(k)
                pages_d[k]={'soup':soup,'status':status}
        no_of_tries+=1
        time.sleep(sleep_time)
    return pages_d,set([v['status'] for k,v in pages_d.items()])



# parses offer data raw data 
def parse_data(data : dict ):
    out_d={}
    out_d['offer_details']={}
    for k,v in data.items():
        tmp_d={}
        if k=='offer_details':
            for l in v:
                if l[1]=="Kup ten pojazd na raty":
                    continue
                tmp_d[l[0]]=l[1]
            out_d[k].update(tmp_d)
        if k=='wyposazenie' and v is not None:
            out_d[k]=[item[0] for item in v]
        if k=='dealer':
            out_d[k]=[item[0] for item in v]
        if k=='loc':
            out_d[k]=v
        if k=='cena':
            out_d[k]=v
        if k=='description':
            out_d[k]=v
        if k=='tytul':
            out_d[k]=v
    
    
    return out_d
    



        
   
class oto_offer:
    def __init__(self,link) -> None:
        self.link=link         # link to this offer 
        self.raw_data,self.title=self.get_data()
        self.parsed_data=self.parse_data()  # parsed data 
    
        self.exclude_key_keys=['Oblicz', 'vin','rejestracyjny','napęd','typ nadwozia','liczba miejsc']
        self.include_keys=['oferta od','marka pojazdu','model pojazdu','generacja','rok','przebieg','pojemnosc','rodzaj paliwa','moc','skrzynia biegow','liczba drzwi','kolor','rodzaj koloru','data pierwszej rejestracji w historii pojazdu','zarejestrowany w polsce']
        self.key_data=self.get_key_data()
        
    def get_data(self):
        raw_data=get_data_from_offer(self.link)
        logging.info(f'got raw data for {json.dumps(raw_data, indent=4, sort_keys=False)}')
        title=raw_data['tytul']
        return raw_data,title
    
    def parse_data(self):
        d=parse_data(self.raw_data)
        return d 

    def get_key_data(self):
        key_data=self.parse_data()['offer_details']
        key_data.update({'tytul':self.title})
        key_data.update({'url':self.link})
        key_data.update({'cena':self.raw_data['cena']})
        tmp_d={}
        for k,v in key_data.items(): # remove non key elements 
            if any([ x.lower() in k.lower() for x in self.exclude_key_keys]):
                continue # pop anything that resemblex exclude keys 
            else:
                tmp_d[k]=v
        return tmp_d





def main():
    OFFERS_LIST='https://www.otomoto.pl/osobowe/mini?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Ato%5D=40000'
    soup=get_soup(OFFERS_LIST)      # 1. get soup 
    pages=get_no_of_pages(soup)     # 2. get all pages 
    df = None 
    for url in pages:
        soup=get_soup(url)
        offers=get_links_from_site(soup) # 3. get links from site
        for link in offers:
            oo=oto_offer(link=link)
            if df is None:
                df=pd.DataFrame(oo.key_data,index=[0])
            else:
                df.loc[len(df)]=oo.key_data

    df.to_csv('./data/oo.csv',sep='\t',index=False,mode='w',header=True)
    tabulated_df = tabulate(df, headers='keys', tablefmt='pipe', showindex=False)
    with open('./data/oo_tabulated.csv', 'w', encoding='utf-8') as f:
        f.write(tabulated_df)
    return 

    
def get_offers_from_offers_url(OFFERS_URL,N=None):
    pages_soup,status=get_soup(OFFERS_URL)                   # get sooup of your search 
    pages_links=get_no_of_pages(pages_soup)               # get links to all pages 
    fetch_d_pages,s=parallel_fetch_nicely(pages_links)      # fetch pages 
    offers_links=[]
    for k,v in fetch_d_pages.items():
        soup=v['soup']
        links=get_links_from_site(soup)                     # get links from each page
        offers_links+=links
    if N is not None: # download less for testing 
        links=links[:N]    
    
    fetch_d_offers,s=parallel_fetch_nicely(offers_links)      # fetch offers
    return fetch_d_offers,s 
    
def parse_offers(fetch_d_offers):
    df = None 
    for k,v in fetch_d_offers.items():

        soup=v['soup']
        logging.warning(f'parsing {k} {soup}' )
        raw_data=get_data_from_offer(soup=soup)
        parsed_data=parse_data(raw_data) # need to parse this thing here 
        logging.info(f'got key data for {json.dumps(parsed_data, indent=4, sort_keys=False)}')
        if df is None:
            df=pd.DataFrame(parsed_data,index=[0])
        else:
            df.loc[len(df)]=oo.key_data
        
    return df 
       
       
if __name__=='__main__': 
    OFFERS_URL='https://www.otomoto.pl/osobowe/mini?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Ato%5D=40000'
    offers_fetch_d,s=get_offers_from_offers_url(OFFERS_URL,N=2)

    df=parse_offers(offers_fetch_d)
    print(df)
    
    exit(1)
    
    pages_soup,status=get_soup(OFFERS_LIST)                   # get sooup of your search 
    pages_links=get_no_of_pages(pages_soup)               # get links to all pages 
    fetch_d_pages,s=parallel_fetch_nicely(pages_links)      # fetch pages 
    offers_links=[]
    for k,v in fetch_d_pages.items():
        soup=v['soup']
        links=get_links_from_site(soup)                     # get links from each page
        offers_links+=links
    
    fetch_d_offers,s=parallel_fetch_nicely(offers_links)      # fetch offers
    print(s)
    print(len(offers_links))
    
    exit(1)
    
    main_parallel(OFFERS_LIST=OFFERS_LIST)
    exit(1)
        
    oo=oto_offer(link=OFFER_DETAILS_URL)
    # pretty print raw data 
    print(json.dumps(oo.key_data, indent=4, sort_keys=False))
