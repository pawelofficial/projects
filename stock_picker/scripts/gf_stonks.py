import requests 
from bs4 import BeautifulSoup
import pandas as pd

def get_google_finance_data(stock_symbol):
    url = f"https://www.google.com/finance/quote/{stock_symbol}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Example: Extracting the stock price
    price = soup.find('div', class_='YMlKec fxKbKc').text

    # dump soup to file 
    with open('./tmp/soup.txt','w',encoding="utf-8") as f:
        f.write(soup.prettify())
    
    return price
    


def get_google_finance_data_multiple(
    symbols={'AAPL:NASDAQ':'AAPL','MSFT:NASDAQ':'MSFT', 'AMZN:NASDAQ':'AMZN', 'GOOG:NASDAQ':'GOOG' }
    ):
    prices_d = {}
    for k,v in symbols.items():
        price = get_google_finance_data(k).replace('$','')
        prices_d[v] = price

    # cast to df 
    df = pd.DataFrame(list(prices_d.items()), columns=['Stock', 'Price'])
        
    return df

if __name__=='__main__':
    df=get_google_finance_data_multiple()
    print(df)