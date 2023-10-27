# Import necessary libraries
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import logging 
import unidecode
import plotly.express as px
logging.basicConfig(level=logging.DEBUG,filemode='w'
                    ,format='%(asctime)s - %(levelname)s - %(message)s'
                    ,filename='./logs/dash_app_v2.log')

# global variables
# lambda function for between operator 
lambda_between = lambda x,values: x.between(float(values[0]) ,float(values[1]) )
# lambda function for in operator 
lambda_in = lambda x,values: x.isin(values)



# cleaning df 
def clean_df(df):
    logging.info('cleaning df')
    clean_string= lambda s: s.strip().replace(' ','_').lower()
    df.columns=[clean_string(unidecode.unidecode(x)) for x in df.columns]           # unidecode and floorelize_ column names 
    dtypes=df.dtypes                                                                # save dtypes for later 
    for c in df.columns:                                                            # unidecode values 
        col_type=dtypes[c]
        if col_type=='object':
            df[c]=[unidecode.unidecode(str(x)) for x in df[c]]
        if col_type in ['int64','float64']:
            df[c]=[float(x) for x in df[c]]
    return df 

# Getting df 
def get_df(fp='./data/oo.csv',sep='\t',url=None):
    logging.info(f' getting df  from url {url}')
    
    df=pd.read_csv(fp,sep=sep,infer_datetime_format=True,index_col=0)   
    print(df.columns)
    logging.info(f'got df of shape {df.shape} ' )
    df=clean_df(df)
    return df 



def make_fig(df,col_mapping_d,filters_d):
    for k,v in filters_d.items():
        fun=v[1] 
        vals=v[0]
        df=df[fun(df[k],vals)]
    fig = px.scatter_3d(df, x=df[col_mapping_d['X']], y=df[col_mapping_d['Y']], z=df[col_mapping_d['Z']],color=df[col_mapping_d['COLOR']] )
    return fig     

# Initialize the Dash app
initial_url='https://www.otomoto.pl/osobowe/alfa-romeo/mito?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=created_at_first%3Adesc'
app = dash.Dash(__name__)

# app layout
#--------------------------------------------------------------------------------------------------------------------------------
app.layout = html.Div([html.Br()
    ,html.Div('No data available', id='error-message', style={'color': 'red'})
    ,html.Label('Search URL:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-search-url', type='text', value=f'{initial_url}',style={'width': '600px'} )
    
    ,html.Br()
    ,html.Label('cena from:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-cena-from', type='text', value='0')
    ,html.Label('cena to:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-cena-to', type='text', value='100000')    
    
    ,html.Br()
    ,html.Label('Przebieg from:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-przebieg-from', type='text', value='0')
    ,html.Label('Przebieg to:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-przebieg-to', type='text', value='99999999')
    
    ,html.Br()
    ,html.Label('rok produkcji from:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-rok-produkcji-from', type='text', value='1969')
    ,html.Label('rok produkcji to:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-rok-produkcji-to', type='text', value='2137')
    
    ,html.Br()
    ,html.Label('moc from:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-moc-from', type='text', value='50')
    ,html.Label('moc to:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-moc-to', type='text', value='300')    

    ,html.Br()
    ,html.Label('marka:', style={'marginRight': '10px'})
    ,dcc.Dropdown(
        id='dropdown-marka'
        ,options=[]  # data [ {'label': 'Option 1', 'value': 'value1'},  {'label': 'Option 2', 'value': 'value2'}... ]
        ,multi=True
        ,value=[]    # initial  
    )


    ,html.Br()
    ,html.Button('Generate Data', id='generate-data-btn', n_clicks=0)
    ,html.Button('Refresh Display', id='refresh-display-btn', n_clicks=0)
    ,dcc.Graph(id='3d-scatter-plot')
    
    ,dcc.Store(id='data-store', data={'random_data': []})
])

# generate callback 
#--------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    [Output('data-store', 'data')
     , Output('error-message', 'children')
     ,Output('dropdown-marka', 'options')
     ]
    ,[Input('generate-data-btn', 'n_clicks')]
    ,[State('input-box-search-url', 'value')]
    ,prevent_initial_call=True
)
def generate_data(n_clicks,url):
    if n_clicks > 0:
        df=get_df(url=url)
        marka_vals=df['marka_pojazdu'].unique()
        marka_options=[{'label': x, 'value': x} for x in marka_vals]    
        return {'random_data': df.to_dict('records')}, 'Data generated',marka_options
    return dash.no_update, dash.no_update


# refresh callback 
#--------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('3d-scatter-plot', 'figure')
    ,[Input('refresh-display-btn', 'n_clicks')]
    ,[
      State('data-store', 'data')
     ,State('input-box-przebieg-from', 'value')
     ,State('input-box-przebieg-to', 'value')
     ,State('input-box-rok-produkcji-from', 'value')
     ,State('input-box-rok-produkcji-to', 'value')
     ,State('input-box-moc-from', 'value')
     ,State('input-box-moc-to', 'value')
     ,State('input-box-cena-from', 'value')
     ,State('input-box-cena-to', 'value')
      ]
    ,prevent_initial_call=True
)
def display_data(n_clicks, data, input_przebieg_from,input_przebieg_to,input_rok_produkcji_from,input_rok_produkcji_to
                 ,input_moc_from,input_moc_to,input_cena_from,input_cena_to
                 , col_mapping_d={'X':'przebieg','Y':'cena','Z':'rok_produkcji','COLOR':'moc'}):
    logging.info(f'refresh display clicked')
    ctx=dash.callback_context
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    logging.info(f'refresh button clicked {input_id}')
    filters_d={'przebieg': [ [input_przebieg_from,input_przebieg_to], lambda_between] 
               ,'rok_produkcji': [ [input_rok_produkcji_from,input_rok_produkcji_to], lambda_between]
               ,'moc': [ [input_moc_from,input_moc_to], lambda_between]
               ,'cena': [ [input_cena_from,input_cena_to], lambda_between]
               }
    logging.info(f'filters_d {filters_d}')
    if n_clicks > 0:
        df = pd.DataFrame(data['random_data'])
        # Check if data is empty
        if df.empty:
            return dash.no_update
        fig = make_fig(df,col_mapping_d,filters_d )
        return fig
    return dash.no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

