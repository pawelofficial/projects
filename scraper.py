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
import ast 

from PIL import Image
from io import BytesIO


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
        #print('element not found')
        logging.warning(f'element not found {tag} {attrs}')
        return None, None,None
    
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
        
    return output_list,div_text,div_element

    # cleans up list of list if it has two items
def get_image_urls(soup):
    #soup = BeautifulSoup(html, 'html.parser')
    image_urls = []

    # Find the picture element
    picture = soup.find('picture')
    if picture:
        # Find all source elements
        sources = picture.find_all('source')
        for source in sources:
            # Get the srcset attribute from each source
            srcset = source.get('srcset')
            # Assuming the srcset could contain multiple URLs, we split them
            urls = srcset.split(',')
            # Extract each URL and add it to the image_urls list
            for url in urls:
                url = url.strip().split(' ')[0]  # Get the URL part before the space
                if url not in image_urls:
                    image_urls.append(url)

        # Finally, get the URL from the img element as a fallback
        img = picture.find('img')
        if img:
            img_url = img.get('src')
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)

    return image_urls


# returns links to all pages with offers 
def get_no_of_pages(soup):
    class_='ooa-1oll9pn er8sc6m7'
    data,txt,_=get_tag_contents(soup
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
def get_data_from_offer(soup
                        ,master_tags_dict={'offer_details': 'content-details-section'}
                        ) -> list:
    offer_data={}
    # put url into offer_Data 
    meta_tag = soup.find('meta', {'property': 'og:url'})
    link = meta_tag['content'] if meta_tag else None
    offer_data['url']=link
    
    # find offer details  
    class_=master_tags_dict['offer_details']
    offer_details,_,_=get_tag_contents(soup
                    ,tag='div'
                    ,attrs={'data-testid': class_}
                    ,sub_tags=['p','a'])
    scraper_asyncio_logger.info(f'offer_details: {offer_details}')
    
    
    offer_details=clean_offer_details(offer_details)
    offer_data['offer_details']=offer_details
    
    class_='ooa-1xhj18k eqdspoq2'
    price,_,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['h3']
                           )
    price=price[0][0].replace(' ','').replace('PLN','')
    offer_data['cena']=price
    # find description 
    class_='ooa-0 e1336z0n1'
    _,desc,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['div']
                           )
    offer_data['description']=desc
    # find wyposazenie 
    class_='ooa-0 e1ic0wg10'
    data,_,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['p']
                           )
    offer_data['wyposazenie']=data
    
    # informacje o delaerze
    class_='ooa-yd8sa2 ern8z620'
    data,_,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['p']
                           )
    offer_data['dealer']=data

    # lokalizacja 
    class_='ooa-1i43dhb ep9j6b60'
    data,txt,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['a']
                           )

    result = re.sub(r'\..+?\}', '', data[0][0] )
    offer_data['loc']=result

    # title

    class_='ooa-1821gv5 ezl3qpx1'
    data,txt,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['h3']
                           )
    title=txt
    offer_data['tytul']=title
    
#    class_='ooa-1p5ldw e1ejyjdh15'
#    data,txt,_=get_tag_contents(soup
#                           ,tag='h3'
#                           ,attrs={'class': class_}
#                           ,sub_tags=['a']
#                           )
#
#    offer_data['pic']=data
#    
    # for every key check whether it is none 
    for k,v in offer_data.items():
        if v is None:
            logging.warning(f'key {k} is None')
            print(f'key {k} is None')


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
    
    # enforce keys - some offerst dont have stuff 
    enforce_keys=['wyposazenie','description']
    
    for key in enforce_keys:
        if key not in out_d.keys():
            if key =='wyposazenie': # wyposazenie is special since its a string that looks like a list 
                out_d[key]='[]'
            else:
                out_d[key]=''
    
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
    scraper_asyncio_logger.info(f'clean_offer_details offer_details  : {offer_details}')
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



async def get_offers_from_offers_url(OFFERS_URL,N=None):
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


def get_images_my_friend(soup):
    script = soup.find('script', {'id': '__NEXT_DATA__'})
    json_text = script.string 
    data = json.loads(json_text)
    images_urls= data['props']['pageProps']['advert']['images']['photos']
    images_d={}
    for d in images_urls:
        # fetch each image 
        url=d['url']
        images_d['url']=url
        response=requests.get(url)
        # put img into d 
        images_d['img']=Image.open(BytesIO(response.content))
        # save all images to data/images dir 
        images_d['img'].save(f'./data/images/img.png')
    return images_d

    
# dumping dictionary to json 
def dump_json(data, filename):
    # ensure dictionary keys are strings 
    data = {str(k): str(v) for k, v in data.items()}
    with open(filename, 'w',encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
def denormalize_df(df=None,columns=['dealer']):
    
    if df is None:
        df=pd.read_csv('./data/new_oo.csv',sep='\t',encoding='utf-8')
    df=df.copy()
    for c in columns:
        df[c] = df[c].apply(ast.literal_eval)
        df=df.explode(c)
    return df 

# loading json to dictionary
def load_json(filename):
    d=json.load(open(filename,encoding="utf-8"))
    return d 




# scrape images 
###if __name__=='__main__':
###    offer_url='https://www.otomoto.pl/osobowe/oferta/volkswagen-beetle-super-stan-navi-ID6FW0Oy.html'
###    offers_url='https://www.otomoto.pl/osobowe/volkswagen/beetle--new-beetle/od-2014?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000&search%5Bfilter_float_year%3Ato%5D=2014'
###    offers_url='https://www.otomoto.pl/osobowe/volkswagen/beetle--new-beetle?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000'
###
###    
###    
###    offers_fetch_d,s=asyncio.run(get_offers_from_offers_url(offers_url))
###    for k,v in offers_fetch_d.items():
###        soup=v['soup']
###        #images_d=get_images_my_friend(soup)
###        a,b,c=get_tag_contents(soup,tag='script',attrs={'id': '__NEXT_DATA__'})
###        print(c)    
###        #print(images_d)
###        input('wait')
###    
###
###    exit(1)
###    script = soup.find('script', {'id': '__NEXT_DATA__'})
###    



    
if __name__=='__main__': 
    #links=open('./data/links.txt','r',encoding="utf-8").readlines()
    #links=[l.strip() for l in links][:5] 
    #asyncio.run(fetch_all(links))
    offers_url='https://www.otomoto.pl/osobowe/alfa-romeo/mito?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=created_at_first%3Adesc'
    offers_url='https://www.otomoto.pl/osobowe/alfa-romeo/mito?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=created_at_first%3Adesc'
    offers_url='https://www.otomoto.pl/osobowe/volkswagen/beetle--new-beetle?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000'
    offers_fetch_d,s=asyncio.run(get_offers_from_offers_url(offers_url))
    
    
    dump_json(offers_fetch_d,'./data/offers_fetch_d.json')

    
    df=parse_offers(offers_fetch_d)
    df.to_csv('./data/new_oo.csv',index=False,sep='\t',encoding='utf-8')

    # write to file as tabulated 
    with open('./data/new_oo_tab.txt','w') as f:
        f.write(tabulate(df, headers='keys', tablefmt='psql'))
        f.close()