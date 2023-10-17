import requests
from bs4 import BeautifulSoup
import pandas as pd 
from tabulate import tabulate
import numpy as np 
from pandas.plotting import parallel_coordinates


def get_soup(url):
    response = requests.get(url,timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup 


# scrapes links with a keyword from a website 
def get_links_from_site(soup,keyword='osobowe/oferta') -> list:
    #soup=get_soup(url)
    links = []
    for link in soup.find_all('a', href=True):
        if keyword in link['href']:
            full_link = f"{link['href']}"        
            if full_link not in links:    # dont add duplicates
                links.append(full_link)
    return links


def get_tag_contents(soup
                     ,tag='div'
                    ,attrs={'data-testid': 'advert-details-list'}
                    ,sub_tag='p'
                     ) -> list :
    contents=[]
    div_element=soup.find(tag, attrs)
    if div_element is None:
        return None 
    
    for st in div_element.find_all(sub_tag):
        contents.append(st.get_text(strip=True))
    return contents 







def get_data_from_offer(url):
    response = requests.get(url,timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')

    div_element = soup.find('div', {'data-testid': 'advert-details-list'})
    p_elements = div_element.find_all('p')

    keys=['Rok produkcji','cena','Przebieg','Moc','tytul','Pojemność skokowa','Rodzaj paliwa','Data pierwszej rejestracji w historii pojazdu','Zarejestrowany w Polsce','url']
    d={k:'' for k in keys}

    for no,p in enumerate(p_elements):
        value = p.get_text(strip=True)
        if value in list(d.keys()):
            next_value = p_elements[no+1].get_text(strip=True)
            d[value]=next_value
            
    #print(d)
    
    # find cena 
    soup = BeautifulSoup(response.text, 'html.parser')
    div_element = soup.find('h3', {'class': 'offer-price__number esicnpr5 ooa-17vk29r er34gjf0'})
    val=div_element.get_text(strip=True)
    d['cena']=val
    
    # find title 
    soup = BeautifulSoup(response.text, 'html.parser')
    div_element = soup.find('h3', {'class': 'offer-title big-text e1aiyq9b1 ooa-ebtemw er34gjf0'})
    val=div_element.get_text(strip=True)
    d['tytul']=val
    
    
    d['url']=url

    return d     

def pagination(url):
    response = requests.get(url,timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')
    # <li aria-label="Page 2" class="pagination-item ooa-1xgr17q"
    div_element = soup.find_all('li', {'class': 'pagination-item ooa-1xgr17q'})
    pages=[''] # first page is current page and 
    for p in div_element:
        pages.append(p.get_text(strip=True))
        
    last_page=pages[-1] # dots in website hwen to many pages ! 
    my_pages=['']
    my_pages+=[str(i) for i in range(2,int(last_page)+1)]
    
    return my_pages
    

    
def write_offers(df):
    with open('./offers.txt','a') as f:
        # write number of offers and current timestamp 
        
        f.write(f'{len(df)}---{pd.Timestamp.now()}\n' )
        
def read_offers():
    with open('./offers.txt','r') as f:
        lines=f.readlines()
    last_line=lines[-1]
    no_of_offers,last_check= last_line.split('---')
    return no_of_offers,last_check    

#    print(h3_element.get_text(strip=True))

#if __name__ == "x__main__":
#    df=pd.read_csv('./alfa.csv',sep='|')
#    write_offers(df)
#    x=read_offers()
#    print(x)
#    exit(1)


def process_tab_df():
    df=pd.read_csv('./alfa.csv',sep='|',infer_datetime_format=True)
    tmp_df=pd.DataFrame(columns=df.columns) # no data 
    for no,row in df.iterrows():
        d=row.to_dict()
        d['Rok produkcji']=int(d['Rok produkcji'])
        d['Przebieg']=int(d['Przebieg'].replace('km','').replace(' ',''))
        d['Moc']=int(d['Moc'].replace('KM','').replace(' ',''))
        d['cena']=int(d['cena'].replace(' ','').replace('PLN',''))
        d['Pojemność skokowa']=int(d['Pojemność skokowa'].replace('cm3','').replace(' ',''))
        tmp_df.loc[len(tmp_df)]=d
    
    return tmp_df 

def calculate_stats(df,column):
    # calulate min,max,mean,median,std on a column 
    min_val=df[column].min()
    max_val=df[column].max()
    mean_val=df[column].mean()
    median_val=df[column].median()
    std_val=df[column].std()
    return min_val,max_val,mean_val,median_val,std_val


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0  # or another appropriate value
    normalized_value = (value - min_val) / (max_val - min_val)
    return normalized_value


def makes_stats_df(df
                   ,stats_cols=['cena','Przebieg','Moc','Rok produkcji']
                   ,out_cols=['tytul'] # add those to output columns 
                   ):
    # make stats_df columns 
    calc_cols=[]
    for c in stats_cols:
        calc_cols.append(f'{c}-to-mean')
    cols=calc_cols + ['cena','Rok produkcji','Przebieg','Moc','Pojemność skokowa','url']
    
    stats_df=pd.DataFrame(columns=['score']+ cols + out_cols) # no data 
    
    
    for no,row in df.iterrows():
        d=row.to_dict()
        for col in stats_cols:
            min_val,max_val,mean_val,median_val,std_val = calculate_stats(df,col)
            colname=f'{col}-to-mean'
            d[colname]=   (d[col] - mean_val) / ( max_val - min_val)
        d['score']=np.sum([d[c] for c in calc_cols])
            
        stats_df.loc[len(stats_df)]=d
    


    stats_df.to_csv('./stats_df.csv',sep='|',index=True,mode='w',header=True)
    
    with open('./stats_df_tabulate.csv', 'w', encoding='utf-8') as f:
        s = tabulate(stats_df, headers='keys', tablefmt='pipe', showindex=False)
        f.write(s)
    
    
        




    
if __name__ == "__main__":
    #links.append('https://www.otomoto.pl/osobowe/oferta/hyundai-i20-asystent-pasa-ruchu-grzane-fotele-i-kierownica-jak-nowy-ID6FxOMT.html')
    # clear alfa.csv 

    URL='https://www.otomoto.pl/osobowe/opel/corsa?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_door_count%5D%5B0%5D=2&search%5Bfilter_enum_door_count%5D%5B1%5D=3&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=filter_float_price%3Adesc&search%5Badvanced_search_expanded%5D=true'
    URL='https://www.otomoto.pl/osobowe/renault/clio/od-2015?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_door_count%5D%5B0%5D=2&search%5Bfilter_enum_door_count%5D%5B1%5D=5&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=filter_float_price%3Adesc&search%5Badvanced_search_expanded%5D=true'
    #URL='https://www.otomoto.pl/osobowe/od-2012?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_door_count%5D%5B0%5D=2&search%5Bfilter_enum_door_count%5D%5B1%5D=3&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=filter_float_price%3Adesc&search%5Badvanced_search_expanded%5D=true'
    pages=pagination(URL)

    N=0
    for p in pages:
        if p !='':
            url=URL+f'&page={p}'
        else:
            url=URL
        print(url)
    
        links = get_links_from_site(url)
        links=list(set(links))
    
        data=[]
        for no,link in enumerate(links):
            
            print(link)
            try:
                d=get_data_from_offer(link)
                data.append(d)
                df=pd.DataFrame(data)
            except:
                print('dupa ! ', link)
                df.to_csv('./byl_error.csv',sep='|',index=False,mode='w',header=True)
            #if no>2:
            #    break

        # write df to file if first time mode w else append 
        if N==0:
            df.to_csv('./alfa.csv',sep='|',index=False,mode='w',header=True)
        else:
            df.to_csv('./alfa.csv',sep='|',index=False,mode='a',header=False)
        N+=1
    
    

    df=pd.read_csv('./alfa.csv',sep='|')
    df=df.sort_values(by='Rok produkcji')
    tabulated_df = tabulate(df, headers='keys', tablefmt='pipe', showindex=False)
    
    # Write to a .txt file
    with open('./alfa_tabulated.csv', 'w', encoding='utf-8') as f:
        f.write(tabulated_df)
        
        
if __name__=='__main__':
    df=process_tab_df()
    makes_stats_df(df)
    exit(1)    