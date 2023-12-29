from snowflake.snowpark import Session
import pandas as pd 
from yf_stonks import * 
from matplotlib import pyplot as plt

connection_parameters = {
    "account": "iytaeuh-zz13343",
    "user": "iza",
    "password": "!QA2ws3ed",
    "role": "ACCOUNTADMIN",  # optional
    "warehouse": "COMPUTE_WH",  # optional
    "database": "DEV",  # optional
    "schema": "DEV",  # optional
  }  

def show_df(df,coly='CLOSE',colx='DATE'):
    df=pd.DataFrame(df)
    fig,ax=plt.subplots()
    ax.plot(df[colx],df[coly],'o')
    plt.show()

# build a sesssion
new_session = Session.builder.configs(connection_parameters).create()  

# quey stats table

q="""SELECT date, close FROM stats WHERE TICKER='SINX';"""
df = new_session.sql(q).collect()

show_df(df)
