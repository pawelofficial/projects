from my_pgsql import mydb
import asyncio 
from coinbase_api import * 
from signals import * 
from indicators import *
# class for doing stuff on postgresql in a loop 
class looper:
    def __init__(self) -> None:
        self.mypgsql=mydb()
        self.auth=CoinbaseExchangeAuth()
        self.ca=coinbase_api(self.auth)    
        self.ca.asset_id='BTC-USD'
        
        self.loop_funs=[self.load_live_data, self.calculate_signals]
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



    async def load_live_data(self):

        candle=self.ca.fetch_last_candle()
        df=pd.DataFrame.from_dict(candle['parsed_data'])
        df['timestamp']=df['timestamp'].astype(str)
        self.mypgsql.write_df(df=df,table='live_data',if_exists='append')
        await asyncio.sleep(30)
        
    async def calculate_signals(self):
        
        df=self.mypgsql.execute_select(''' 
                        select  start_epoch, start_time as timestamp, open, close, low, high, volume from vw_agg5 order by start_epoch desc limit 200
                        ''' )
        # cast object dtypes to float  in loop 

        for col in list(df.columns):
            if df[col].dtype=='object':
                df[col]=df[col].astype('float64')

        signal,s_df=signals().signal_wave2(df=df)
        # delete last row from signals prior to writing data if its timestamp is matching incoming row to refresh last candle  

        # if s_df is not empty 
        print(s_df)
        if not s_df.empty:
            
            this_ts=s_df['start_epoch'].max() 
            q=f"delete from signals where start_epoch={this_ts}"
            self.mypgsql.execute_dml(q)
        
        self.mypgsql.write_df(df=s_df.iloc[[0]],table='signals',if_exists='append',only_last_row=True) # write last row 
        
        # quantiles 
        i=indicators(df=df)
        print(i.df)
        
        if not i.df.empty:
            i.bucketize_df() 
            this_ts=i.df['start_epoch'].max()
            # delete last row from quantiles proor to writing data
            q=f"delete from quantiles where start_epoch={this_ts}"
            self.mypgsql.execute_dml(q)
            
        self.mypgsql.write_df_array(df=i.df.iloc[[0]],tbl='quantiles'
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
    
