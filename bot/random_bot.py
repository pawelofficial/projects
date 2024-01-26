
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
        self.trade_quant=0.001
        
        self.Client=Client
        self.api_key,self.api_secret=self.read_secrets()
        self.client=self.Client(self.api_key,self.api_secret)

        self.order_dic={'symbol':None,'side':None,'quantity':None,'price':None,'ts':None,'candle_ts':None,'order':None}
        # make trade_df dataframe from order dic
        self.trade_df=pd.DataFrame([self.order_dic])
        self.cur_candle=None # cur candle 
        self.server_time=self.client.get_server_time()
        self.interval='5m'
        self.last_trade_ts=None

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
    def make_decision_dummy(self,N=10):
        decision=random.randint(0,N-1)
        if decision==0:
            buy,sell=True,False
        elif decision==1:
            buy,sell=False,True
        else:
            buy,sell=None,None 
        return buy,sell

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

    def trade(self,make_decision,trade_once_per_candle=False, **kwargs):
        
        # if current candle is same as last trade candle, then dont trade 
        cur_candle_ts=self.get_last_candle()['ts']
        if cur_candle_ts==self.last_trade_ts and trade_once_per_candle is True:
            return None 
        
        buy_decision,sell_decision=make_decision(**kwargs)
        if buy_decision is True or sell_decision is True: # buy_decision false means selling
            price=self.check_prices()
            ts=dt.datetime.now()
            
        if buy_decision is True:
            self.order_dic={'symbol':'BTCUSDT','side':'BUY','quantity':self.trade_quant,'price':price,'ts':ts,'candle_ts':cur_candle_ts }
            order=self.market_order(self.order_dic)
            self.trade_df.loc[len(self.trade_df)]={ **self.order_dic,'order':order }
            
        if sell_decision is True:
            self.order_dic={'symbol':'BTCUSDT','side':'SELL','quantity':self.trade_quant,'price':price,'ts':ts,'candle_ts':cur_candle_ts}
            order=self.market_order(self.order_dic)
            self.trade_df.loc[len(self.trade_df)]={ **self.order_dic,'order':order }
        else:
            pass
        
        self.save_trade_df()
        self.last_trade_ts=cur_candle_ts
        #print(self.trade_df,len(self.trade_df))

    # fetches last candle 
    def get_last_candle(self,symbol='BTCUSDT',interval=None,limit=1):
        if interval is None:
            interval=self.interval
        candles=self.client.get_klines(symbol=symbol,interval=interval,limit=limit)
        candle=candles[0]
        # convert candle to dictionary with names of fields 
        candle_dic={'timestamp':candle[0],'open':candle[1],'high':candle[2],'low':candle[3],'close':candle[4],'volume':candle[5]}
        # convert timestamp to datetime 
        candle_dic['timestamp']=dt.datetime.fromtimestamp(candle_dic['timestamp']/1000)
        candle_dic['ts']=candle_dic['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        return candle_dic

    # method for saving trade_df to csv file 
    def save_trade_df(self,fp='./logs/trade_df.csv'):
        self.trade_df.to_csv(fp,index=True,sep=',',quotechar='"')
        return None


# sub class - randombot 
class RandomBot(TradingBot):
    def __init__(self, name):
        super().__init__(name)
        
    def trade(self):
        while True:
            f= self.make_decision_dummy
            super().trade(make_decision=f,trade_once_per_candle=False)
            print(self.trade_df,len(self.trade_df))

        
        

        
    
        
if __name__=='__main__':
    rb=RandomBot('randombot')
    rb.trade()
    while True:
        f=rb.make_decision_dummy
        rb.trade(make_decision=f)
        
        time.sleep(1)

#    print(p)
    
#s    rb.query_live_data()