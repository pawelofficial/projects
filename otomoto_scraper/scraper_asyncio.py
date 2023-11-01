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
import unidecode 
import datetime
import time 

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename='./logs/scraper_asyncio.log')

# Get the specific logger for scraper
scraper_asyncio_logger = logging.getLogger('scraper_asyncio')
scraper_asyncio_logger.info('Logging from the scraper module')


# regular funs 
# parses soup to get links of pages 
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

# returns links to all pages with offers 
def get_no_of_pages(soup):
    class_='ooa-1oll9pn er8sc6m7'
    data,txt=get_tag_contents(soup
                    ,tag='div'
                    ,attrs={'class': class_}
                    ,sub_tags=['li'])
    meta_tag = soup.find('meta', {'property': 'og:url'})
    link = meta_tag['content'] if meta_tag else None
    
    if data is None:
        return [link]
    
    max_page=max([int(d[0]) for d in data if d[0].isdigit()])
    all_links=[link]
    for no in range(2,max_page+1):
        all_links.append(link+f'&page={no}')
    
    return all_links
    
# scraping the data
def get_data_from_offer(soup) -> list:
    offer_data={}
    # put url into offer_Data 
    meta_tag = soup.find('meta', {'property': 'og:url'})
    link = meta_tag['content'] if meta_tag else None
    offer_data['url']=link
    
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
    
# parses offer data raw data 
def parse_data(data : dict ):
    out_d={}
    # log data 
    scraper_asyncio_logger.info(f'parsing data: {data}')
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
            if v is not None:
                out_d[k]=v.replace('\n', '').replace('\r', ' ')
            else :
                out_d[k]=''
        if k=='tytul':
            out_d[k]=v
        if k=='url':
            out_d[k]=v
    # log parsed data
    scraper_asyncio_logger.info(f'parsed data: {out_d}')
    return out_d
    



    
    # flattens and unidecodes parsed data 

def flatten_parsed_data(parsed_data):
    lambda_unidecode = lambda x: unidecode.unidecode(x)
    key_data_d={}
    for k,v in parsed_data.items(): # remove non key elements
        k=lambda_unidecode(k)
        # if v is a string 
        if isinstance(v,str):
            v=lambda_unidecode(v)
        # if v is a list 
        if isinstance(v,list):
            v=[lambda_unidecode(x) for x in v]
        if k =='offer_details':
            key_data_d.update({ lambda_unidecode(k):lambda_unidecode(v) for k,v in v.items()})
        else:
            key_data_d[k]=v
    # treat it so i can plug it into a df 
    for key, value in key_data_d.items():
        if isinstance(value, list):
            key_data_d[key] = str(value)
            
    # log key data d 
    scraper_asyncio_logger.info(f'key data d: {key_data_d}')
    return key_data_d


def parse_offers(fetch_d_offers):
    df = None 
    for k,v in fetch_d_offers.items():
        soup=v['soup']
        raw_data=get_data_from_offer(soup=soup)
        parsed_data=parse_data(raw_data)
        key_data=flatten_parsed_data(parsed_data)
        if df is None:
            df=pd.DataFrame(key_data,index=[0])
        else:
            df.loc[len(df)]=key_data
    return df 

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


# async funs
#---------------------------------------------------------------------------------------------------
async def fetch(url, semaphore):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    async with semaphore:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response

async def fetch_all(urls, max_connections=50):
    semaphore = asyncio.Semaphore(max_connections)
    tasks = [fetch(url, semaphore) for url in urls]
    responses = await asyncio.gather(*tasks)
    return responses

async def parallel_fetch_nicely(urls,max_retries=10,sleep_time=0.1):
    fetch_d={url:{'status':None,'soup':None} for url in urls}
    check_statuses=lambda d: all([v['status']==200 for k,v in d.items()])                    # checks if all statuses are 200
    make_fetch_d =  lambda responses: {r.url: {'status':r.status_code, 'soup': BeautifulSoup(r.text, 'html.parser')  } for r in responses} # parallel fetch into a d from a list 
    ## get urls of fetch_d where status is not 200 
    get_urls_not_200 =  lambda d: [k for k,v in d.items() if v['status']!=200]                 # get urls of fetch_d where status is not 200    
    #parallel_fetch_nicely
    
    fetch_d=make_fetch_d(await fetch_all(urls))
    no=0
    while not check_statuses(fetch_d) and no<=max_retries:
        bad_urls=get_urls_not_200(fetch_d)
        fetch_d.update(make_fetch_d( await fetch_all(bad_urls)))
        scraper_asyncio_logger.info(f'not 200 statuses: {len(bad_urls)}')
        time.sleep(sleep_time)
        no+=1
    return fetch_d,set([v['status'] for k,v in fetch_d.items()])



async def get_offers_from_offers_url(OFFERS_URL,N=5):
    fetch_d,status=await parallel_fetch_nicely([OFFERS_URL])   # fetch main search soup 
    pages_soup=fetch_d[OFFERS_URL]['soup']
    pages_links=get_no_of_pages(pages_soup)                    # get links to all pages 
    scraper_asyncio_logger.info(f'no of pages to scrape : {len(pages_links)}')

    fetch_d_pages,s=await parallel_fetch_nicely(pages_links)   # fetch each page  
    offers_links=[]
    for k,v in fetch_d_pages.items():                          # get each link for an offer 
        soup=v['soup']
        links=get_links_from_site(soup)                     
        offers_links+=links
        
    if N is not None:                                          # download less for testing / trial version  
        offers_links=offers_links[:N]    
    fetch_d_offers,s=await parallel_fetch_nicely(offers_links)      # fetch offers themselves 
    return fetch_d_offers,s 




    
if __name__=='__main__': 
    #links=open('./data/links.txt','r',encoding="utf-8").readlines()
    #links=[l.strip() for l in links][:5] 
    #asyncio.run(fetch_all(links))
    offers_url='https://www.otomoto.pl/osobowe/alfa-romeo/mito?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=created_at_first%3Adesc'
    offers_fetch_d,s=asyncio.run(get_offers_from_offers_url(offers_url))
    df=parse_offers(offers_fetch_d)
    print(df)