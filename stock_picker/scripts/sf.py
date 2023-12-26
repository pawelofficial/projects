import snowflake.connector
import pandas as pd 

import snowflake.connector

# Establish the connection
con = snowflake.connector.connect(
    user='iza',
    password='!QA2ws3ed',
    account='iytaeuh-zz13343',
    warehouse='COMPUTE_WH',
    database='DEV',
    schema='DEV'
)

# Create a cursor object
cur = con.cursor()

# Execute a query
cur.execute('SELECT * FROM stats')

# Fetch the results
rows = cur.fetchall()

# get columns 
cols = [x[0] for x in cur.description]

# cast to df  with cols 
df = pd.DataFrame(rows,columns=cols)




# write df to csv 
fp='C:\\gh\\my_random_stuff\\stock_picker\\scripts\\tmp\\stats.csv'
df.to_csv(fp,index=False,quotechar='"',quoting=1,header=True,sep='|',mode='w')
print('done')


# READ TMPdata.csv 


