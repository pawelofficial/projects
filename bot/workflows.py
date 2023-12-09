from coinbase_api import * 
from indicators import * 
from my_pgsql import * 
from signals import * 

# 1st thing - download data and put it  to pgsql 
def wf__download_data(write_to_pg=True
                      ,start_dt=None
                      ,end_dt=None):
    if start_dt is None:
        # dynamically set start_dt to week ago 
        start_dt=datetime.datetime.now()-datetime.timedelta(days=2)
        start_dt=start_dt.strftime('%d-%m-%Y')
    if end_dt is None:
        # dynamically set end_dt to tomorrow 
        end_dt=datetime.datetime.now()+datetime.timedelta(days=1)
        end_dt=end_dt.strftime('%d-%m-%Y')
    
    auth=CoinbaseExchangeAuth()
    ca=coinbase_api(auth)    
    df,fp=ca.bulk_download_data(
                            start_dt=start_dt # DD-MM-YYYY
                           ,end_dt=end_dt   # DD-MM-YYYY
                           ,granularity=60
                           ,to_df=True
                           #to_csv=True,fname='raw_data.csv'
                           )
    if write_to_pg:
        p=mydb()
        p.execute_dml('truncate table historical_data')
        p.execute_dml('truncate table live_data')              # be careful with this one 
        p.write_df(df=df,table='historical_data',if_exists='append',deduplicate_on='epoch')
    return fp 
    
    
# 2nd thing - make features and put them to pgsql
def wf__prep_data():
    p=mydb()
    df=p.execute_select('select  start_time as timestamp, open, close, low, high, volume from vw_agg5 order by start_epoch asc' )
    # cast open,close,low,high to float64
    df[['open','close','low','high','volume']]=df[['open','close','low','high','volume']].astype('float64')
    # bucketize data 
    i=indicators(df=df)
    i.bucketize_df() 
    p.execute_dml('drop table quantiles')
    ddl=p.df_to_ddl(df=df[i.basic_columns],table_name='quantiles',extra_cols=[('ar','integer[]')  ])
    p.execute_dml(ddl)
    p.write_df_array(df=i.df,tgt_ar_col='ar',tbl='quantiles',df_ar_cols=i.quantile_columns,df_base_cols=i.basic_columns)
    

    # compute and  write signals - basic + signal columns 
    p.execute_dml('drop table signals')
    signal,s_df=signals().signal_wave2(df=i.df[i.basic_columns])


    ddl=p.df_to_ddl(df=s_df,table_name='signals' )
    p.execute_dml(ddl)
    print(s_df)
    p.write_df(df=s_df,table='signals',if_exists='append')

    
    
if __name__=='__main__':
    #wf__download_data()
    wf__prep_data()