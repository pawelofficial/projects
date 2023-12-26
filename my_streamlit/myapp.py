import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt

### call sf.py with os package  to download csv from sf 
#import os
#os.system('python3 C:\\gh\\my_random_stuff\\stock_picker\\scripts\\sf.py')


# read csv from scripts/tmp
fp='C:\\gh\\my_random_stuff\\stock_picker\\scripts\\tmp\\stats.csv'

df=pd.read_csv(fp,sep='|',quotechar='"',quoting=1) # first 100 rows are stupid
# cast DATE column to datetime
df['DATE']=pd.to_datetime(df['DATE'])

# filter out first 100 days 
df=df[df['DATE']>'2020-01-01'].copy()

# vars 
basic_columns=[ 'DATE','OPEN','CLOSE','LOW','HIGH','VOLUME']
GREEN_THRESHOLD=-2
RED_THRESHOLD=2

# rename columns according to map_dic
map_dic={'Z_COMB':'Z_COMB','PRANK_SUM':'CHEAP_INDICATOR2'}
df=df.rename(columns=map_dic)

# ------------------- chepaest stocks right now - calculate today_df  -------------------#
# filter on max date 
filter_date=df['DATE'] == max(df['DATE'])
# filter on CHEAO_INDICATOR1
filter_ci1=df['Z_COMB']<=0.05

tmp_df=df[filter_date]
# order by CHEAP_INDICATOR1
tmp_df=tmp_df.sort_values(by='Z_COMB',ascending=True)

# make a today_df which is a df with highest date
highlight_columns = ['Z_COMB','Z10','Z25','Z50','Z100']  # Replace with your actual columns
_=['TICKER'] + highlight_columns + basic_columns 

today_df=df[df['DATE']==max(df['DATE'])].copy().sort_values('Z_COMB',ascending=True)

#------------------- sidebar -------------------#
# make stocks list, ordered by Z_COMB 
stocks=today_df['TICKER'].tolist()


default_stock=today_df['TICKER'].tolist()[0]
default_index = stocks.index(default_stock) if default_stock in stocks else 0
STOCK=st.sidebar.selectbox('choose stock',stocks,index=default_index)




lower_bound = st.sidebar.number_input('Enter lower bound for green color', value=-2)
upper_bound = st.sidebar.number_input('Enter upper bound for red color', value=2)


import pandas as pd
import streamlit as st

def highlight_survived(s):
    return ['background-color: green']*len(s) if s.Survived else ['background-color: red']*len(s)

def color_survived(val):
    if val < lower_bound:
        color = '#8BC34A'  # Light Green
    elif val > upper_bound:
        color = '#F44336'  # Red
    else:
        color = '#FFEB3B'  # Yellow
    return f'background-color: {color}'


st.dataframe(today_df[ _].style.applymap(color_survived, subset=highlight_columns))







#------------------- candlestick chart  -------------------#
tmp_df=df[df['TICKER']==STOCK].copy()
tmp_df['DATE']=pd.to_datetime(tmp_df['DATE'])

# order tmp_df by date 
tmp_df=tmp_df.sort_values(by='DATE',ascending=True)
today_filter=tmp_df['DATE']==max(tmp_df['DATE'])

import plotly.graph_objects as go

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
# -------------------- cheap indicator historgram  -------------------#
which_stocks = st.radio('Which stocks:', (f'{STOCK}','All' ))

if which_stocks == 'All':
    tmp_df = df.copy()
else:
    filter = df['TICKER'] == STOCK
    tmp_df = df[filter].copy()


colors = ['red', 'blue', 'green', 'purple','orange']
hist_cols=['Z10', 'Z25', 'Z50', 'Z100','Z_COMB']
# today values of STOCK 





today_filter = tmp_df['DATE'] == max(tmp_df['DATE'])

today_dic = tmp_df[today_filter][hist_cols].to_dict('records')[0]

fig, ax = plt.subplots()
for col, color in zip(hist_cols, colors):
    ax.hist(tmp_df[col], bins=100, alpha=0.5, label=col, color=color)
    ax.set_facecolor('lightgray')


color_dict = dict(zip(['Z10', 'Z25', 'Z50', 'Z100','Z_COMB'], colors))

offset = - ax.get_ylim()[1] / 10  # Adjust this value as needed
for i, (label, value) in enumerate(today_dic.items()):
    ax.axvline(value, color=color_dict.get(label, 'k'), linestyle='--')
    ax.text(value, ax.get_ylim()[1] + i * offset, f'{round(value,2)}', rotation=0, verticalalignment='top', color=color_dict.get(label, 'k'))
# add title 



ax.legend()

fig



# -------------------- some stats -------------------#
# order tmp_df by date 
ticker_filter=tmp_df['TICKER']==STOCK
tmp_df=tmp_df[ticker_filter].copy()
tmp_df=tmp_df.sort_values(by='DATE',ascending=True)

cols=df.columns.tolist()
chosen_cols=['CLOSE','Z10']
chosen_cols = st.multiselect('Select options:', cols, default=['CLOSE','SMA10','Z_COMB'])

normalize = st.radio('Normalize data:', ('No', 'Yes'))
if normalize == 'Yes':
    normalize = True
else:
    normalize = False


fig, ax1 = plt.subplots()

# Create a second y-axis that shares the same x-axis
ax2 = ax1.twinx()

for col in chosen_cols:
    if 'z' in col:
        ax = ax2  # Plot on the second y-axis
        marker = 'o'
    else:
        ax = ax1  # Plot on the first y-axis
        marker = 'x'
    
    if normalize:
        ax.plot(tmp_df['DATE'], (tmp_df[col] - tmp_df[col].min()) / (tmp_df[col].max() - tmp_df[col].min()), marker, label=col)
    else:
        ax.plot(tmp_df['DATE'], tmp_df[col], marker, label=col)

# Add a legend for each y-axis
ax1.legend(loc='upper left')

ax1.set_ylabel('Non-z columns')
ax2.set_ylabel('z columns')

# add title to the fig 
fig.suptitle(f'{STOCK} daily stats')

 
fig


