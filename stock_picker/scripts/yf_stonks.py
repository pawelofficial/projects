import requests
import pandas as pd
import datetime
from datetime import datetime as dt
from bs4 import BeautifulSoup
import time 
from io import StringIO
import os 
import logging 


# Create a logger
logger = logging.getLogger(os.path.basename(__file__))
# Set the log level to INFO
logger.setLevel(logging.INFO)
# Create a file handler
handler = logging.FileHandler('./tmp/yf_stonks.log',mode='w')
# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Add the handlers to the logger
logger.addHandler(handler)
# Use the logger
logger.info(f'starting {os.path.basename(__file__)}')




def get_stock_data(symbol
                   , interval= None 
                   ,start_date=None
                   ,end_date=None
                   ,project_fp='C:\gh\my_random_stuff'
                   ,rel_fp='stock_picker\seeds'
                   ,do_write=True
                   ,mode='w'
                   ,header=True
                   ,fname=None
                   ,cols=['TICKER', 'DATE','OPEN','CLOSE','LOW','HIGH','VOLUME']
                   ):
    logging.info(f"getting data for {symbol} from {start_date} to {end_date} with interval {interval} with backup setting {do_write} ")
    if start_date is None:
        # 6 months from now 
        start_date = (datetime.datetime.now() - datetime.timedelta(days=360)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if interval is None:
        interval = '1d'
    
    
    period1 = int(time.mktime(dt.strptime(start_date, "%Y-%m-%d").timetuple()))
    period2 = int(time.mktime(dt.strptime(end_date, "%Y-%m-%d").timetuple()))

    url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    logger.info(f"requesting data from {url}")

    response = requests.get(url,headers=headers)
    logger.info(f"response.status_code: {response.status_code}")

    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))
        data.columns = [x.upper() for x in data.columns]
        data['TICKER']=symbol
        logger.info(f"got df of shape: {data.shape}")

    else:
        logger.warning(f"uh oh ! response.status_code: {response.status_code} ")
        data= None
        logger.warning(f" ticker {symbol} not found ")

    
    
    
    if do_write and data is not None:
        # rename columns to uppercase 

        fname=fname or symbol
        fname=f"{fname}.csv"
        fp=os.path.join(project_fp,rel_fp,fname)
        logger.info(f"writing data to {fp}")
        data[cols].to_csv(fp,index=False,quotechar='"',quoting=1,header=header,sep='|',mode=mode)



# function writing down the data 


from bs4 import BeautifulSoup
import requests

def get_nasdaq_symbols():
    all_symbols=[]
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        print(letter)
        url = f"https://eoddata.com/stocklist/NASDAQ/{letter}.htm"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'quotes'})
        symbols = [row.find('td').text for row in table.find_all('tr')[1:]]
        all_symbols+=symbols
    
    # write down the symbols
    with open('./tmp/nasdaq_symbols.txt','w') as f:
        f.write('\n'.join(all_symbols))
    return symbols

def read_symbols():
    with open('./tmp/nasdaq_symbols.txt','r') as f:
        symbols=f.read().split('\n')
    return symbols




stonks=read_symbols()[:50]

mode='w'
header=True
for stonk in stonks:
    get_stock_data(stonk,mode=mode,header=header,fname='data')
    time.sleep(2)
    mode='a'
    header=False
    



