from my_pgsql import mydb
import asyncio 
from coinbase_api import * 
from signals import * 
from indicators import *
from utils import * 
# class for doing stuff on postgresql in a loop 
class looper:
    def __init__(self) -> None:
        self.mypgsql=mydb()
        self.auth=CoinbaseExchangeAuth()
        self.ca=coinbase_api(self.auth)    
        self.ca.asset_id='BTC-USD'
        self.logger=setup_logging2(name='looper.log')
        
        self.loop_funs=[self.load_live_data,self.calculate_signals]
        self.run_tasks=True
    # loads live data from coinbase api to pgsql
    async def main(self):
        while self.run_tasks:
            tasks = [asyncio.create_task(fun()) for fun in self.loop_funs]
            try:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=300)  # Run for 5 minutes
            except asyncio.TimeoutError:
                print('exiting asyncio')
                for task in tasks:
                    task.cancel()  # Cancel the tasks if they run for more than 5 minutes
            # Add a condition to break the loop if necessary
            # if condition:
            #     break
            await asyncio.sleep(30)  # Add a small delay before the next iteration to prevent high CPU usage


    # deletes last row from a table if it matches df 
    def delete_last_matching_row(self,df,table,column='epoch'):
        # if df is empty dont do that 
        if df.empty:
            return
        
        last_ts=df[column].max().astype(int)
        q=f"delete from {table} where {column}='{last_ts}'"
        self.mypgsql.execute_dml(q)
        log_stuff2(self.logger,msg=f'deleting last row from live_data table at ts {last_ts}')

    async def load_live_data(self):
        candle=self.ca.fetch_last_candle()
        df=pd.DataFrame.from_dict(candle['parsed_data'])
        df['timestamp']=df['timestamp'].astype(str)
        
        self.delete_last_matching_row(df=df,table='live_data',column='epoch')
        self.mypgsql.write_df(df=df,table='live_data',if_exists='append')
        log_stuff2(self.logger,msg=f'inserting row to live_data table at epoch {df["epoch"].max()} ')

        
    async def calculate_signals(self):
        
        df=self.mypgsql.execute_select(''' 
            with cte as ( 
                select  start_epoch, start_time as timestamp, open, close, low, high, volume from vw_agg5 order by start_epoch desc limit 500 
                )
                select * from cte 
                order by start_epoch;
            ''' )
        
        
        
        # cast object dtypes to float  in loop 

        for col in list(df.columns):
            if df[col].dtype=='object':
                df[col]=df[col].astype('float64')

        signal,s_df=signals().signal_wave2(df=df)
        # delete last row from signals prior to writing data if its timestamp is matching incoming row to refresh last candle  

        # if s_df is not empty 

        self.delete_last_matching_row(df=s_df,table='signals',column='start_epoch')
        log_stuff2(self.logger,msg=f'inserting row to signals table at epoch {s_df["start_epoch"].max()} ')

        self.mypgsql.write_df(df=s_df.iloc[[-1]],table='signals',if_exists='append',only_last_row=True) # write last row 

        # quantiles 
        i=indicators(df=df)
        i.bucketize_df(order_desc_col='start_epoch') 
        print(i.df)
        # DUMP I.DF TO FILE
        i.dump_df(cols=['start_epoch'] + i.quantile_columns ,fname='quantiles_df')
        
        
        self.delete_last_matching_row(df=i.df,table='quantiles',column='start_epoch')            
        log_stuff2(self.logger,msg=f'inserting row to quantiles table at epoch {i.df["start_epoch"].max()} ')

        self.mypgsql.write_df_array(df=i.df.iloc[[-1]],tbl='quantiles'
                                    ,tgt_ar_col='ar'
                                    ,df_ar_cols=i.quantile_columns
                                    ,df_base_cols=i.basic_columns
                                    ,truncate_load=False
                                    ,only_last_row=False
                                    )

        
if __name__=='__main__':
    l=looper()
#    l.calculate_signals()

    
    asyncio.run(l.main())
#    asyncio.run(l.calculate_signals())
