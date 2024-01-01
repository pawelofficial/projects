# Import python packages
import streamlit as st  
from snowflake.snowpark import Session
import matplotlib.pyplot as plt
from snowflake.snowpark.functions import col
import pandas as pd
import plotly.graph_objects as go
import time 
import numpy as np
from snowflake.snowpark.context import get_active_session
connection_parameters = {
    "account": "iytaeuh-zz13343",
    "user": "iza",
    "password": "!QA2ws3ed",
    "role": "ACCOUNTADMIN",  # optional
    "warehouse": "COMPUTE_WH",  # optional
    "database": "DEV",  # optional
    "schema": "DEV",  # optional
  }  

#session = Session.builder.configs(connection_parameters).create()  
# Try to get an existing active session

#session = Session.builder.configs(connection_parameters).create()
# Try to get an existing active session
try:
    session = get_active_session()
except Exception as e:
    session = None 
# If there is no active session, create a new one
if session is None:
    session = Session.builder.configs(connection_parameters).create()


def create_or_read_object(**kwargs):
    key=kwargs['key']
    val=kwargs['val']
    # if val is df 
    if isinstance(val,pd.DataFrame): # if its df 
        bl=(True if key in st.session_state else False) and val.equals(st.session_state[key]) # if key exists and val is the same
    else:
        bl=(True if key in st.session_state else False) and val == st.session_state[key]
    
    print(f'-- - - - - -bl is {bl} for {key}')
    
    
    if bl: # if key exists and val is the same
        print(f'reading {key} from session state')
        return st.session_state[key]
    else:
        print(f'creating {key} in session state')
        st.session_state[key]=val
        return val


# vars 
STATS_COLUMNS=['Z_COMB','Z10','Z25','Z50','Z100'] 
BASIC_COLUMNS=[ 'DATE','OPEN','CLOSE','LOW','HIGH','VOLUME']

# write session id 
# ---------------------------------------------------- sessions are weird
st.write(f'session id: {id(session)}')


st.title("Cheap Stocks picker")
st.write(""" 
Cheap stocks are those whose z-values are low, you can look at them here.
""")
#------------------- get data  -------------------#
# cache today df 
#@st.cache_resource(hash_funcs={Session: id})
def get_today_df(session,how_many=100):
    session.sql(f""" insert into cnt(cnt) values (1)""" ).collect()
    df = session.sql(f"""
    with today_stats as (
        select ticker,max(date) date  from stats group by all 
        )
    , first_stocks as ( 
    select  s1.* ,current_timestamp() as cts, 'chepaest' as type
    from stats s1 
    inner join today_stats s2 
        on s1.ticker=s2.ticker
        and s1.date=s2.date
    where s1.z_comb is not null -- z comb is null for the first day of the stock
    order by z_comb asc 
    limit {how_many} 
    )
    , last_stocks as ( 
    select  s1.* ,current_timestamp() as cts, 'expensive' as type
    from stats s1 
    inner join today_stats s2 
        on s1.ticker=s2.ticker
        and s1.date=s2.date
    where s1.z_comb is not null 
    order by z_comb desc 
    limit {how_many} 
    )
    select * from first_stocks 
    union all 
    select * from last_Stocks 
    order by type, z_comb
    """).collect()
    #df=df.to_pandas() # this should be cached so the app runs faster 
    return df 





def color_survived(val):
    if val < lower_bound:
        color = '#8BC34A'  # Light Green
    elif val > upper_bound:
        color = '#F44336'  # Red
    else:
        color = '#FFEB3B'  # Yellow
    return f'background-color: {color}'

def get_ticker_df(session,STOCK):
    # IF STOCK IS A LIST 
    if isinstance(STOCK,list):
        STOCK = ','.join(f"'{item}'" for item in STOCK)
        s=f"""
            select * from STATS where  ticker in ({STOCK})
            """
        df = session.sql(s).collect()
        return df 
    
    
    df = session.sql(f"""
    select * from STATS where  ticker='{STOCK}'
    """).collect()

    #df=df.to_pandas() # this should be cached so the app runs faster 
    return df

# caching today df 
TODAY_DF=create_or_read_object(key='TODAY_DF',val=get_today_df(session))


STOCK=st.sidebar.selectbox('choose stock',TODAY_DF,index=0)
lower_bound = st.sidebar.number_input('cheap std ', value=-2.0, step=-0.5)
upper_bound = st.sidebar.number_input('expensive std', value=2.0, step=0.5)

# cache ticker df if sidebar stock is changed
if 'TICKER_DF' not in st.session_state or STOCK != st.session_state['TICKER_STOCK']:
    TICKER_DF=get_ticker_df(session,STOCK)
    st.session_state['TICKER_DF']=TICKER_DF
    st.session_state['TICKER_STOCK']=STOCK
    print(f'creating ticker_df for  {STOCK}')
else:
    TICKER_DF=st.session_state['TICKER_DF']
    TICKER_STOCK=st.session_state['TICKER_STOCK']
    print(f'reading ticker df from cache for {STOCK}')    


_=['TICKER'] + STATS_COLUMNS + BASIC_COLUMNS + ['CTS']
st.dataframe(pd.DataFrame(TODAY_DF)[_].style.applymap(color_survived, subset=STATS_COLUMNS))


#------------------- candlestick chart  -------------------#
import plotly.graph_objects as go
tmp_df=pd.DataFrame(get_ticker_df(session,STOCK))
fig = go.Figure(data=[go.Candlestick(x=tmp_df['DATE'],
                                     open=tmp_df['OPEN'],
                                     high=tmp_df['HIGH'],
                                     low=tmp_df['LOW'],
                                     close=tmp_df['CLOSE'])])

fig.update_xaxes(
    rangeslider_visible=False,
    dtick="M1"  # Monthly dticks 
 
)
fig.update_layout(
    title=f'{STOCK} daily chart'
)
fig

# -------------------- historgram  -------------------#
st.write('**histogram of z values**')



     # stock first in radio order  
which_stocks=create_or_read_object(key='which_stock_index',val=1)
which_stocks = st.radio('Which stocks:',(f'{STOCK}','All'),index=which_stocks)

tickers = [row['TICKER'] for row in TODAY_DF]
hist_df=create_or_read_object(key='hist_df',val=pd.DataFrame(get_ticker_df(session,tickers)))

if which_stocks==STOCK:
    tmp_df=pd.DataFrame(TICKER_DF)
else:
    tmp_df=hist_df
    
hist_cols=['Z10', 'Z25', 'Z50', 'Z100','Z_COMB']


cur_stocks = [row for row in TODAY_DF if row['TICKER'] == STOCK]
_ = cur_stocks[0].asDict()
today_dic={k:v for k,v in _.items() if k in hist_cols} # vertical lines showing today value

# -------------------- some stats -------------------#

# make histogram 
colors = ['red', 'blue', 'green', 'purple','orange']
fig, ax = plt.subplots()
for col, color in zip(hist_cols, colors):
    ax.hist(tmp_df[col], bins=100, alpha=0.5, label=col, color=color)
    ax.set_facecolor('lightgray')
    
    
# make vertical lines on histogram 
color_dict = dict(zip(hist_cols, colors))
offset = - ax.get_ylim()[1] / 10  # Adjust this value as needed
for i, (label, value) in enumerate(today_dic.items()):
    ax.axvline(value, color=color_dict.get(label, 'k'), linestyle='--')
    ax.text(value, ax.get_ylim()[1] + i * offset, f'{round(value,2)}', rotation=0, verticalalignment='top', color=color_dict.get(label, 'k'))
# add vertical lines for lower_bound and upper_bound 


ax.axvline(lower_bound, color='white', linestyle='-.')
ax.axvline(upper_bound, color='white', linestyle='-.')
ax.axvline(lower_bound, color='white', linestyle='-.')
ax.axvline(upper_bound, color='white', linestyle='-.')
ax.legend()
fig

# -------------------- hodl curves -------------------#
if 'z_metric' not in st.session_state:
    z_metric=st.selectbox('choose z-metric',STATS_COLUMNS,index=0)
    st.session_state['z_metric']=z_metric
else:
    z_metric=st.session_state['z_metric']
    # index 
    z_metric=st.selectbox('choose z-metric',STATS_COLUMNS,index=STATS_COLUMNS.index(z_metric))
    st.session_state['z_metric']=z_metric


# reminiscent of old logic, lets keep it here for now 
hodl_s=','.join(f"'{item}'" for item in tickers)
hodl_s=f"where ticker in ({hodl_s})"

z_comb_lower = st.text_input("z_comb_lower",round(today_dic[z_metric],2) )
z_comb_delta = st.text_input("hodl z_comb delta ",0.5)
z_comb_lower=float(z_comb_lower)
z_comb_delta=float(z_comb_delta)

# build a query 
uber_query=f"""
with ag as (
select ticker ag_ticker ,max(close) as max_close, min(close) as min_close
from stats
group by ag_ticker
)
, cte as (
select {z_metric} AS METRIC, case when METRIC between {str(z_comb_lower - z_comb_delta) } and {str(z_comb_lower+z_comb_delta) } then 1 else 0 end as islow
, (CLOSE - min_close) / ( max_close - min_close) as norm_close,close  
, DATE , TICKER
from stats 
inner join ag 
    on stats.ticker=ag.ag_ticker
{hodl_s}
),cte2 as (
select METRIC, TICKER, norm_close,close , islow,  max(islow) over (PARTITION BY TICKER  order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW ) as next_ten
,date
 from cte
 order by date
)
,cte3 as (
 select METRIC, norm_close,close , islow, next_ten, next_ten*sum(next_ten) over (PARTITION BY TICKER   order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as hodl_start  ,date
,TICKER
from cte2
order by date
)
,CTE4 AS (
select METRIC, norm_close,close , islow, next_ten
, case when hodl_Start = 1 then 1 else 0 end as hodl_startt
, next_ten*sum(hodl_startt) over (PARTITION BY TICKER  order by date) as which_event
, sum(next_ten) over (PARTITION BY TICKER  order by date ) as next_ten_sum
,date
,TICKER
from cte3
order by date
)
,cte5 as (
select METRIC, norm_close,close ,islow,next_ten,hodl_startt,which_event,next_ten_sum*next_ten as pre_index
,next_ten*lag(next_ten_sum,1) over (PARTITION BY TICKER  order by date ) as lagged_sum
,date
,TICKER
from cte4
order by date
)
,helpful_cte as (
select TICKER, which_event,min(lagged_sum) as min_lagged_sum
from cte5
group by all
order by 1
),cte6 as  (
select
cte5.*
,hcte.min_lagged_sum
from cte5
left join helpful_cte hcte
    on cte5.which_event = hcte.which_event
    AND CTE5.TICKER = HCTE.TICKER
order by date
), CTE7 AS (
select cte6.*
,pre_index-min_lagged_sum as index
from  cte6
order by TICKER,date
)
SELECT METRIC,TICKER, DATE, norm_close,close , INDEX , HODL_STARTT HODL_START, NEXT_TEN
FROM CTE7
ORDER BY TICKER,DATE
-- when hodl start == 1 then hodl starts
-- in snowpark  loop over which_event to get your series !
;
"""


hodl_df=create_or_read_object(key='hodl_df',val=pd.DataFrame(session.sql(uber_query).collect()))


# Find indices where INDEX is 0
indices = np.where(hodl_df['INDEX'] == 0)[0]

fig, ax = plt.subplots()

# Plot each series separately
start = 0
for index in indices:
    ax.plot(hodl_df['INDEX'].iloc[start:index], hodl_df['NORM_CLOSE'].iloc[start:index], '-.')
    start = index
ax.plot(hodl_df['INDEX'].iloc[start:], hodl_df['NORM_CLOSE'].iloc[start:], '-.')

fig

stock_filter=hodl_df['TICKER']==STOCK
indices = np.where(hodl_df[stock_filter]['INDEX'] == 0)[0]


fig, ax = plt.subplots()

# Plot each series separately
start = 0
for index in indices:
    ax.plot(hodl_df[stock_filter]['INDEX'].iloc[start:index], hodl_df[stock_filter]['NORM_CLOSE'].iloc[start:index], '-.')
    start = index
ax.plot(hodl_df[stock_filter]['INDEX'].iloc[start:], hodl_df[stock_filter]['NORM_CLOSE'].iloc[start:], '-.')

fig


