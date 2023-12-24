import requests
import pandas as pd
import datetime
from datetime import datetime as dt
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
                   ,cols=['Date','Open','Close','Low','High','Volume']
                   ):
    logging.info(f"getting data for {symbol} from {start_date} to {end_date} with interval {interval} with backup setting {do_write} ")
    if start_date is None:
        start_date = '2023-01-01'
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
    else:
        logger.warning(f"uh oh ! response.status_code: {response.status_code} ")
        data= pd.DataFrame()

    logger.info(f"got df of shape: {data.shape}")
    
    
    if do_write:
        fname=f"{symbol}.csv"
        fp=os.path.join(project_fp,rel_fp,fname)
        logger.info(f"writing data to {fp}")
        data[cols].to_csv(fp,index=False,quotechar='"',quoting=1,header=True,sep='|')


# function writing down the data 





df = get_stock_data('AAPL')



