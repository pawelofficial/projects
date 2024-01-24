
from my_pgsql import mydb
import random 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import json 
import pandas as pd 
from utils import setup_logging2
import datetime as dt
import time 
# setup logging 
bot_logger=setup_logging2('bot_logger')
bot_logger.info('bot_logger is set up')




# super class for all bots  of name tradingbot
class TradingBot:
    def __init__(self, name):
        self.name = name
        self.mypgsql=mydb()
        self.mypgsql.ping()
        
        self.Client=Client
        self.api_key,self.api_secret=self.read_secrets()
        self.client=self.Client(self.api_key,self.api_secret)

    # read secrets 
    def read_secrets(self,fp='./secrets/secrets.json'):
        secrets_dic=json.load(open(fp,'r'))
        return secrets_dic['binance_api_key'],secrets_dic['binance_api_secret']
    
    # queries live data table to get last row of data 
    def query_live_data(self,sql=None):
        if sql is None:  # by default simply query last row of live data 
            sql="""
            select * from live_data hd 
            where timestamp = ( select max ( timestamp) from live_data  hd2 )
            """
        df=self.mypgsql.execute_select(sql)
        return df 
    
    # makes decision whether to sell or buy ( True ), sell ( False ), do nothing None   
    def make_decision_dummy(self,df,N=10):
        decision=random.randint(0,N-1)
        if decision==0:
            return True 
        elif decision==1:
            return False 
        else:
            return None

    # checks cur price of a symbol 
    def check_prices(self,symbol='BTCUSDT'):
        prices = self.client.get_all_tickers()     
        if symbol is not None:
            price = [ p for p in prices if p['symbol']==symbol ][0]['price']
            return price 
        return prices 
    
    def market_order(self,order_dic):
        if order_dic['side']=='BUY':
            order = self.__market_buy(order_dic)
        elif order_dic['side']=='SELL':
            order = self.__market_sell(order_dic)
        return order 
    
    def __market_buy(self,order_dic):
        order = self.client.create_test_order(
            symbol=order_dic['symbol'],
            side=self.Client.SIDE_BUY,
            type=self.Client.ORDER_TYPE_MARKET,
            quantity=order_dic['quantity'])        
        return order 
    
    def __market_sell(self,order_dic):
        order = self.client.create_test_order(
            symbol=order_dic['symbol'],
            side=self.Client.SIDE_SELL,
            type=self.Client.ORDER_TYPE_MARKET,
            quantity=order_dic['quantity'])        
        return order
    
    # shows you your current balances - ones youre interested in and ones that are not zero 
    def check_account_balance(self,symbols=['BTC','USDT']):
        info=self.client.get_account()
        info_assets={}
        info_nonzero_assets={}
        for d in info['balances']:
            
            if d['asset'] in symbols:
                info_assets[d['asset']]={'free':d['free'],'locked':d['locked']}
            if float(d['free'])>0:
                info_nonzero_assets[d['asset']]={'free':d['free'],'locked':d['locked']}
        return info_assets, info_nonzero_assets


# sub class - randombot 
class RandomBot(TradingBot):
    def __init__(self, name):
        super().__init__(name)  
        self.order_dic={'symbol':None,'side':None,'quantity':None,'price':None,'ts':None,'order':None}
        # make trade_df dataframe from order dic
        self.trade_df=pd.DataFrame([self.order_dic])
        self.trade_quant=0.001
        
        
    def trade(self):
        df=self.query_live_data()
        print(df)
        buy_decision=self.make_decision_dummy(df)
        if buy_decision is True or buy_decision is False:
            price=self.check_prices()
            # current timestamp 
            ts=dt.datetime.now()
            
        if buy_decision is True:
            self.order_dic={'symbol':'BTCUSDT','side':'BUY','quantity':self.trade_quant,'price':price,'ts':ts }
            order=self.market_order(self.order_dic)
            self.trade_df.loc[len(self.trade_df)]={ **self.order_dic,'order':order }
            
            
        if buy_decision is False:
            self.order_dic={'symbol':'BTCUSDT','side':'SELL','quantity':self.trade_quant,'price':price,'ts':ts}
            order=self.market_order(self.order_dic)
            self.trade_df.loc[len(self.trade_df)]={ **self.order_dic,'order':order }
            
        else:
            pass
        
        print(self.trade_df,len(self.trade_df))
        
    
        
if __name__=='__main__':
    rb=RandomBot('randombot')
    print(1)
    while True:
        rb.trade()
        
        time.sleep(1)

#    print(p)
    
#s    rb.query_live_data()