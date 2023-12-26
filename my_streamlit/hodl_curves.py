import pandas as pd 
import matplotlib.pyplot as plt

fp='C:\\gh\\my_random_stuff\\stock_picker\\scripts\\tmp\\stats.csv'
df=pd.read_csv(fp,sep='|',quotechar='"',quoting=1) # first 100 rows are stupid
# cast DATE column to datetime
df['DATE']=pd.to_datetime(df['DATE'])

# filter out first 100 days 


# vars 
basic_columns=['TICKER', 'DATE','OPEN','CLOSE','LOW','HIGH','VOLUME','CHEAP_INDICATOR1']

# rename columns according to map_dic
map_dic={'Z10':'CHEAP_INDICATOR1','PRANK_SUM':'CHEAP_INDICATOR2'}
df=df.rename(columns=map_dic)

# choose stock 
STOCK='SINX'
tmp_df=df[df['TICKER']==STOCK].copy()
# order by date and reset index 
tmp_df=tmp_df.sort_values(by=['DATE'])
tmp_df.reset_index(inplace=True,drop=True)

# have a bool column 
tmp_df['bool']=tmp_df['CHEAP_INDICATOR1']>0


 

# plot thing
fig, ax = plt.subplots(2,1)
ax[0].plot(tmp_df['DATE'],tmp_df['CLOSE'],'-o')
ax[1].plot(tmp_df.index,tmp_df['bool'],'-o')

plt.show() 