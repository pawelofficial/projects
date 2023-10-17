import requests
from bs4 import BeautifulSoup
import pandas as pd 
from tabulate import tabulate
import numpy as np 
from pandas.plotting import parallel_coordinates
import re 
import json
import logging 
logging.basicConfig(level=logging.INFO,filemode='w',filename='./logs/tests.log',format='%(asctime)s - %(levelname)s - %(message)s')

OFFERS_LIST='https://www.otomoto.pl/osobowe/renault/clio/od-2015?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=filter_float_price%3Adesc&search%5Badvanced_search_expanded%5D=true'
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
    return soup 

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
def get_data_from_offer(url) -> list:
    soup=get_soup(url)
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
    offer_data['price']=price
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
    offer_data['title']=title
    
    
    
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
        if k=='price':
            out_d[k]=v
        if k=='description':
            out_d[k]=v
        if k=='title':
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
        title=raw_data['title']
        return raw_data,title
    
    def parse_data(self):
        d=parse_data(self.raw_data)
        return d 

    def get_key_data(self):
        key_data=self.parse_data()['offer_details']
        key_data.update({'title':self.title})
        key_data.update({'url':self.link})
        key_data.update({'price':self.raw_data['price']})
        tmp_d={}
        for k,v in key_data.items(): # remove non key elements 
            if any([ x.lower() in k.lower() for x in self.exclude_key_keys]):
                continue # pop anything that resemblex exclude keys 
            else:
                tmp_d[k]=v
        return tmp_d

#d oo.csv and ump as tabulate 
###df=pd.read_csv('./data/oo.csv',sep='\t',encoding="utf-8")
###tabulated_df = tabulate(df, headers='keys', tablefmt='pipe', showindex=False)
###with open('./data/oo_tabulated.csv', 'w', encoding='utf-8') as f:
###    f.write(tabulated_df)
###    
###exit(1)




def main():
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

       
if __name__=='__main__': 
    main()
    exit(1)
        
    oo=oto_offer(link=OFFER_DETAILS_URL)
    # pretty print raw data 
    print(json.dumps(oo.key_data, indent=4, sort_keys=False))
