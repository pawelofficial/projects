import pandas as pd 
import numpy as np 
from matplotlib import pyplot as plt
fp='C:\\gh\\my_random_stuff\\stock_picker\\scripts\\tmp\\data.csv'
fp='C:\gh\my_random_stuff\stock_picker\seeds\data.csv'

df=pd.read_csv(fp,sep='|',quotechar='"',quoting=1) # first 100 rows are stupid

# MAKE ARTIFICIAL DATA - SINX 


tmp_df=df[df['TICKER']=='AACG'].copy()

tmp_df['TICKER']='SINX'
# reset index 
tmp_df.reset_index(inplace=True,drop=True)
tmp_df['INDEX']=tmp_df.index

# make  open, close, low, high a  sinx + some noise 
tmp_df['CLOSE']=tmp_df['INDEX'].apply(lambda x: np.sin(x/10) + np.random.normal(0,0.1,1)[0])


#fig,ax=plt.subplots(1,1)
#ax.plot(tmp_df.index,tmp_df['CLOSE'],'-o')
#plt.show()

# remove INDEX COLUMN
tmp_df=tmp_df.drop(columns=['INDEX'])

# append tmp_df to ./data.csv 

tmp_df.to_csv(fp,index=False,header=False,sep='|',quotechar='"',quoting=1,mode='a')