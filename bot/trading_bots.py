
from my_pgsql import mydb
import random 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import json 
import pandas as pd 
from utils import setup_logging2,plot_df
import datetime as dt
import time 
import os 
import torch
from torch_model4 import Network 
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
    
    # checks various times 
    def check_times(self,interval='5m'):
        cur_candle=self.get_last_candle(interval=interval)                           # start time of current candle 
        next_candle=cur_candle['timestamp']+dt.timedelta(minutes=int(interval[:-1])) # wont work for intervals other than minutes
        
        if self.last_trade_ts is None:
            last_trade_to_next_candle=None 
        else:
            last_trade_to_next_candle=(next_candle-self.last_trade_ts).strftime('%Y-%m-%d %H:%M:%S')
        
        dic={'cur_candle':cur_candle['ts']                                                                     # start time of current candle 
             ,'next_candle':next_candle.strftime('%Y-%m-%d %H:%M:%S')                                          # start time of next candle 
             ,'cur_time_to_next_candle':(next_candle-dt.datetime.now()).seconds                                # time to next candle
             ,'last_trade_to_next_candle':last_trade_to_next_candle                                            # time from last trade to next candle
             ,'now':dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')                                            # current time
             ,'last_trade_ts':self.last_trade_ts.strftime('%Y-%m-%d %H:%M:%S') if self.last_trade_ts is not None else None # last trade time
             }
        
        return dic
    
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

    def trade(self,decision_fun):
        while True:
            self.trade(make_decision=decision_fun,trade_once_per_candle=True)
            

    def trade_once(self,make_decision,trade_once_per_candle=False, **kwargs):
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

    # method for saving trade_df to csv file jjj
    def save_trade_df(self,fp='./logs/trade_df.csv'):
        self.trade_df.to_csv(fp,index=True,sep=',',quotechar='"')
        return None


# sub class - randombot 
class RandomBot(TradingBot):
    def __init__(self, name):
        super().__init__(name)

class pgSQLBot(TradingBot):
    def __init__(self, name):
        super().__init__(name)
        
    def make_decision(self): # blah blah blah 
        query='select * from DEV.DEV.VW_AGG5 where start_epoch =( select MAX(start_epoch) from vw_agg5 va );'
        df=self.mypgsql.execute_select(query)
        
        
class torchBot(TradingBot):
    def __init__(self, name):
        super().__init__(name)
        self.models_fp='./models/wave_models/'
        self.model_name='wave_loop.pth'
        self.model=None # torch model 
        self.df=None    # data 
        self.device= torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.query='select * from DEV.DEV.quantiles where start_epoch =( select MAX(start_epoch) from quantiles );'
        self.query='''
                    with cte as ( 
                select  * from quantiles order by start_epoch desc limit 500 
                )
                select * from cte 
                order by start_epoch;
        '''
        
    def read_data(self):
        
        self.df=self.mypgsql.execute_select(self.query)
        self.no_of_features=len(self.df['ar'].iloc[0])
        
    def read_torch_model(self):
        SCALING_FACTOR = 2
        self.model = Network(self.no_of_features, 1, SCALING_FACTOR)
        
        model_fp=os.path.join(self.models_fp,self.model_name)
        self.model.load_state_dict(torch.load(model_fp))
        self.model.eval()
        self.model=self.model.to(self.device)
        

    def predict_one(self,iloc=-1):
        array=self.df['ar'].iloc[iloc]
        tensor=torch.tensor(array).float()
        with torch.no_grad():
            prediction_raw = self.model(tensor)
        prediction=int(round(prediction_raw.item()))
        print(prediction,sum(array),prediction_raw,self.df['start_epoch'].iloc[iloc])
        # update pgsql 
        self.mypgsql.execute_dml(f"update signals set torch_prediction={prediction} where start_epoch={self.df['start_epoch'].iloc[iloc]}")
        
        
    def predict_multiple(self,df=None,col='ar'):
        if df is None:
            df=self.df
        for i in range(len(df)):
            array=df[col].iloc[i]
            tensor=torch.tensor(array).float()
            with torch.no_grad():
                prediction_raw = self.model(tensor)
            prediction=int(round(prediction_raw.item()))
            #print(prediction,prediction_raw,sum(array),df['start_epoch'].iloc[i])
            df.at[i,'torch_prediction']=prediction

        # update data in pgsql 
        self.mypgsql.execute_dml('drop table tmp')  
        print(df)
        self.mypgsql.write_df(df=df,table='tmp',if_exists='append')
        query='''
        update signals set torch_prediction=tmp.torch_prediction 
        from tmp 
        where signals.start_epoch=tmp.start_epoch
        '''        
        self.mypgsql.execute_dml(query)
        
        

def plot_pgsql():
    pgsql=mydb()
    query='select * from signals where torch_prediction is not Null'
    df=pgsql.execute_select(query)
    buy_mask=df['torch_prediction'].astype(int) ==1
    sell_mask=df['wave_signal'].astype(int)==1
    
    # buy and sell columns
    df['buy']=df['open'].where(buy_mask)
    df['sell']=df['open'].where(sell_mask)
    
    print(df['buy'])
    

    
    plot_df(df=df,top_chart_cols=['close'],top_dots=['buy']
                  ,bottom_chart_cols=['close'],bot_dots=['sell']
                  ,top_markers=[ ['^','g'],['v','r'] ]
                  )
            

    
        
if __name__=='__main__':
    plot_pgsql()
    exit(1)
    bot=torchBot('torch')
    bot.read_data()
    bot.read_torch_model()
    bot.predict_multiple()

    exit(1)
    
    rb=pgSQLBot('pgsql')
    rb.make_decision()
    
    exit(1)
    rb.trade()
    while True:
        f=rb.make_decision_dummy
        rb.trade(make_decision=f)
        
        time.sleep(1)

#    print(p)
    
#s    rb.query_live_data()