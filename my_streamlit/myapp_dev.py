import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import pyautogui

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


#------------------- vars -------------------#
BASIC_COLUMNS=[ 'DATE','OPEN','CLOSE','LOW','HIGH','VOLUME']
STATS_COLUMNS=['Z_COMB','Z10','Z25','Z50','Z100'] 
TODAY_DF=df[df['DATE']==max(df['DATE'])].sort_values(by='Z_COMB',ascending=True).copy() # TODAY_DF SORTED BY Z_COMB

STOCK=TODAY_DF['TICKER'].tolist()[0]
TICKER_DF= lambda STOCK : df[df['TICKER']==STOCK].copy() # df for a stock 


#------------------- sidebar / cheap stocks today -------------------#
def change_tuple(tup,val='foo'):
    if tup[0]=='All':           # ('All','sinx')
        tup=(tup[0],val)        # ('All','foo')
    else:                       # ('sinx','All')
        tup=(val,tup[1])        # ('foo','All')     
    return tup

stocks=TODAY_DF['TICKER'].tolist()
default_index = stocks.index(STOCK) if STOCK in stocks else 0

STOCK=st.sidebar.selectbox('choose stock',stocks,index=default_index)
st.session_state['STOCK']=STOCK


lower_bound = st.sidebar.number_input('cheap std ', value=-2.0, step=-0.5)
upper_bound = st.sidebar.number_input('expensive std', value=2.0, step=0.5)

# gotta figure out how to reset sidebar values -> to do 
#if st.sidebar.button('Reset'):
#    pyautogui.hotkey("ctrl","F5")


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

_=['TICKER'] + STATS_COLUMNS + BASIC_COLUMNS 
st.write('**Cheapest stocks today**')
st.dataframe(TODAY_DF[_].style.applymap(color_survived, subset=STATS_COLUMNS))


#------------------- candlestick chart  -------------------#
import plotly.graph_objects as go
tmp_df=TICKER_DF(STOCK)
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



tup = (f'{STOCK}','All')      # stock first in radio order  


if 'which_stock_index' not in st.session_state:
    which_stocks=1            # by default zeroth option is chosen 
else:                         # if session state exists take element from session 
    which_stocks=st.session_state['which_stock_index']

which_stocks = st.radio('Which stocks:',tup,index=which_stocks)


hist_cols=['Z10', 'Z25', 'Z50', 'Z100','Z_COMB']
if which_stocks == 'All':
    tmp_df = df.copy()
    st.session_state['which_stock_index']=1 # write radio index to session 

else:
    tmp_df = tmp_df=TICKER_DF(STOCK)
    st.session_state['which_stock_index']=0 # write radio index to session 
    
# stock filter on today df 
ticker_filter=TODAY_DF['TICKER']==STOCK
today_dic = TODAY_DF[ticker_filter][hist_cols].to_dict('records')[0] # vertical lines showing today value 

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


ax.legend()
fig



# -------------------- some stats -------------------#
st.write(f'**{STOCK} daily chart**')
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
    if 'Z' in col:
        ax = ax2  # Plot on the second y-axis - righthandside
        marker = 'x'
    else:
        ax = ax1  # Plot on the first y-axis
        marker = 'o'
    
    if normalize:
        ax.plot(tmp_df['DATE'], (tmp_df[col] - tmp_df[col].min()) / (tmp_df[col].max() - tmp_df[col].min()), marker, label=col)
    else:
        ax.plot(tmp_df['DATE'], tmp_df[col], marker, label=col)


# Add a legend for each y-axis
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax1.set_ylabel('Non-z columns')
ax2.set_ylabel('z columns')

# add title to the fig 

 
fig


