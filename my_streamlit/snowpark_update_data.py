from snowflake.snowpark import Session
import pandas as pd 
from datetime import datetime as dt
import datetime
import logging 
import requests 
from io import StringIO
import os 
import time

# Create a logger
logger = logging.getLogger(os.path.basename(__file__))
# Set the log level to INFO
logger.setLevel(logging.INFO)
# Create a file handler
handler = logging.FileHandler('./tmp/snowpark_get_data.log',mode='w')
# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Add the handlers to the logger
logger.addHandler(handler)
# Use the logger
logger.info(f'starting {os.path.basename(__file__)}')

connection_parameters = {
    "account": "iytaeuh-zz13343",
    "user": "iza",
    "password": "!QA2ws3ed",
    "role": "ACCOUNTADMIN",  # optional
    "warehouse": "COMPUTE_WH",  # optional
    "database": "DEV",  # optional
    "schema": "DEV",  # optional
  }  

# build a sesssion
new_session = Session.builder.configs(connection_parameters).create()  

# checks last date for a ticker in stats table 
def check_last_dates():
  # quey stats table
  q="""SELECT TICKER, MAX(DATEADD('day', -1, "DATE"))::date::varchar as DATE_STR  FROM DATA GROUP BY ALL;"""
  df = new_session.sql(q).collect()
  df=pd.DataFrame(df)
  return df 

def read_symbols_from_file():
    with open('./tmp/nasdaq_symbols.txt','r') as f:
        symbols=f.read().split('\n')

    # cast symbols into dataframe with date_str=None
    symbols_df=pd.DataFrame(symbols,columns=['TICKER'])
    symbols_df['DATE_STR']='None'

    return symbols_df


def yf_get_stock_data(
    ticker
    ,start_date = None 
    ,end_date  = None 
    ,interval='1d'
    ):
    if start_date is None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=360)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # cast dates to unixtimestamps
    period1 = int(time.mktime(dt.strptime(start_date, "%Y-%m-%d").timetuple()))
    period2 = int(time.mktime(dt.strptime(end_date, "%Y-%m-%d").timetuple()))
    
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))
        data.columns = [x.upper() for x in data.columns]
        data['TICKER']=ticker
        logger.info(f' status code {response.status_code} for ticker {ticker}')
        logger.info(f"got df of shape: {data.shape} for ticker {ticker}")
    else:
        data=None 
        logger.warning(f" ticker {ticker} not found, api response status code: {response.status_code} ")


    return data 


def get_stocks_data(tickers_df
                    ,end_date=None
                    ,cols=['TICKER', 'DATE','OPEN','CLOSE','LOW','HIGH','VOLUME']
                    ,write_to_sf=True
                    ,sf_table='DATA'

                    ):
  data_df=None
  
  if end_date is None:
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")

  mode='w'
  header=True
  for no,row in tickers_df.iterrows():
    ticker=row['TICKER']
    print(ticker)
    start_date = row['DATE_STR']  
    if start_date =='None':        # if tickers_df is loaded from file then date will be none
      start_date=None
    logger.info(f"getting data for {ticker} from {start_date} to {end_date} ")
    # write data to a file 
    tmp_df=yf_get_stock_data(ticker
                   ,start_date = start_date
                   ,end_date = end_date
                   ,interval='1d'
                   )


 
    if tmp_df is not None and write_to_sf is True:  # write to tmp file first 
      # save it to file 
      tmp_df.to_csv(f'./tmp/data.csv',index=False,sep='|',quotechar='"',quoting=1,mode=mode,header=header)
      mode='a'
      header=False
       
  if write_to_sf: # once loop finishes write whole thing to sf 
    tmp_df=pd.read_csv(f'./tmp/data.csv',sep='|',quotechar='"',quoting=1)
    print(tmp_df[cols])
    snowflake_df = new_session.create_dataframe(tmp_df[cols])
    snowflake_df.write.mode("append").save_as_table(sf_table) # write data to snowflake
    logger.info(f"written {tmp_df.shape[0]} rows to {sf_table} table")



if __name__ == "__main__":
    
  tickers_df=check_last_dates()         # get last date for each ticker from snowflake 
  tickers_df=read_symbols_from_file()[:5]  # get tickers from file instead of snowflake 
  data_df=get_stocks_data(tickers_df)   # get data from yahoo finance


#  table_name='DATA'
#  snowflake_df = new_session.create_dataframe(data_df)
#  snowflake_df.write.mode("append").save_as_table(table_name) # write data to snowflake
#  logger.info(f"written {data_df.shape[0]} rows to {table_name} table")



# cd /mnt/c/gh/my_random_stuff/my_streamlit 
# /mnt/c/gh/github_actions/actions-runner/venv/bin/python3 ./snowpark_get_data.py 
