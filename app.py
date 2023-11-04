# Import necessary libraries
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import logging 
import unidecode
import webbrowser
import base64
from itertools import chain
import numpy as np 
import plotly.express as px
import ast
import pandas as pd 
import numpy as np 
import logging 
import asyncio 
import scraper as sa 

import dash_bootstrap_components as dbc
from flask import Flask 
import dash 

logging.basicConfig(level=logging.WARNING, filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename='./logs/dash.log')
#from scraper import * 
# Get the specific logger for dash
dash_logger = logging.getLogger('dash')
dash_logger.info('this is dash ')






# global variables
# lambda function for between operator 
lambda_between = lambda x,values: x.between(float(values[0]) ,float(values[1]) )
# lambda function for in operator 
lambda_in = lambda x,values: x.isin(values)
lambda_in_lst = lambda x, values: x.apply(lambda y: any(value == elem for value in values for elem in ast.literal_eval(y)))


initial_url='https://www.otomoto.pl/osobowe/alfa-romeo/mito?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=created_at_first%3Adesc'
#flask_server=Flask(__name__)
#app = dash.Dash(__name__,server=flask_server,external_stylesheets=[dbc.themes.BOOTSTRAP])
#server=app.server


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server



# gets unique elements from df column where column values are list literals 
def unique_elements(df, column_name):
    # Convert string lists to actual lists
    lists = df[column_name].apply(ast.literal_eval)
    # Flatten lists and find unique elements
    unique_elems = set(chain.from_iterable(lists))
    return unique_elems
# cleaning df 
def clean_df(df):
    dash_logger.info('cleaning df')
    clean_string= lambda s: s.strip().replace(' ','_').lower()
    df.columns=[clean_string(unidecode.unidecode(x)) for x in df.columns]           # unidecode and floorelize_ column names 
    dtypes=df.dtypes                                                                # save dtypes for later 
    #for c in df.columns:                                                            # unidecode values 
    #    col_type=dtypes[c]
    #    if col_type=='object':
    #        df[c]=[unidecode.unidecode(str(x)) for x in df[c]]
    #    if col_type in ['int64','float64']:
    #        df[c]=[float(x) for x in df[c]]
    dash_logger.info(f'df dtypes {df.dtypes}')
    _=df['liczba_drzwi'].unique()
    dash_logger.info(f' unique librze drzwi  {_}')
    for c in df.columns:
        # try to cast stuff to float else unidecode and clean 
        try:
            df[c]=df[c].astype(float)
        except:
            pass
    dash_logger.info(f'df dtypes2 {df.dtypes}')
    _=df['liczba_drzwi'].unique()
    dash_logger.info(f' unique librze drzwi2  {_}')
    # replace columns which are numeric with -1 
    for c in df.columns:
        if df[c].dtype in ['int64','float64']:
            df[c].replace(np.nan,-1, inplace=True)
    # replace non numeric columns with 'nan'
    for c in df.columns:
        if df[c].dtype not in ['int64','float64']:
            df[c].replace(np.nan,'unknown', inplace=True)

    
#    df.replace(np.nan,-1, inplace=True)
    _=df['liczba_drzwi'].unique()
    dash_logger.info(f' unique librze drzwi2  {_}')
    df.to_csv('./data/cleaned_df.csv',sep='\t')
    return df 

# Getting df 
def get_df(fp='./data/new_oo.csv',sep='\t',url=None):
    dash_logger.info(f' getting df  from url {url}')
    
    df=pd.read_csv(fp,sep=sep,infer_datetime_format=True,index_col=0)     
    # parallel fetch my brother in christ ! 
    offers_fetch_d,s=asyncio.run(sa.get_offers_from_offers_url(url))   
    df=df=sa.parse_offers(offers_fetch_d)
    dash_logger.info(f'got df of shape {df.shape} ' )
    dash_logger.info(f' df columns prior to  cleaning are {df.columns}')
    df=clean_df(df)
    dash_logger.info(f' df columns after cleaning are {df.columns}')
    return df 



def make_fig(df,col_mapping_d,filters_d):
    for k,v in filters_d.items():
        fun=v[1] 
        vals=v[0]
        if vals !=[]: # not filtering if nothing was chosen so all data from dccs are displayed by default and ux is no cap fr fr 
            df=df[fun(df[k],vals)]


    fig = px.scatter_3d(df, x=df[col_mapping_d['X']]
                        , y=df[col_mapping_d['Y']]
                        , z=df[col_mapping_d['Z']]
                        ,color=df[col_mapping_d['COLOR']]
                        ,hover_name=df['tytul'].apply(lambda x: ' '.join(x.split()[:4])) # hover title truncated 
                        )
    fig.update_layout(height=800)
    return fig     

def filter_df(df,filters_d):
    tmp_df=df.copy()
    for k,v in filters_d.items():
            fun=v[1] 
            vals=v[0]
            if vals !=[]: # not filtering if nothing was chosen so all data from dccs are displayed by default 
                tmp_df=tmp_df[fun(tmp_df[k],vals)]
    return tmp_df





# app layout
#--------------------------------------------------------------------------------------------------------------------------------
app.layout = html.Div([html.Br()
###    ,html.Div([
###    html.A("Link to external site", href='https://plot.ly', target="_blank")
###    ])             
###    
    ,html.Div('No data available', id='error-message', style={'color': 'red'})
    
    
    ,html.Label('Search URL:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-search-url', type='text', value=f'{initial_url}',style={'width': '600px'} )
    
    ,html.Br()
    ,html.Button('Download otomoto Data', id='generate-data-btn', n_clicks=0)
    ,html.Br()
    ,html.A('Download Data to your kąkuter', id='download-link', href="#")  # Initial link setup

    ,html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
            ,'display': 'none'         # disabling upload for now 
        },
        multiple=False  # Allow single file
    ),
    html.Div(id='output-data-upload')
    ,dcc.Store(id='data-store-upload', data={'random_data': []})
    ])

    
    
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

    , html.Div([
            html.Label('marka:', style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='dropdown-marka',
                options=[],
                multi=True,
                value=[],
                style={'width': '95%'}  # gpt generated line: set the dropdown width to 95% of the containing Div
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'width': '1000px'})  # gpt generated line: set the Div width to 1000px

    , html.Div([
            html.Label('model:', style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='dropdown-model',
                options=[],
                multi=True,
                value=[],
                style={'width': '95%'} 
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'width': '1000px'}) 
    , html.Div([
            html.Label('skrzynia biegow:', style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='dropdown-skrzynia-biegow',
                options=[],
                multi=True,
                value=[],
                style={'width': '95%'} 
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'width': '1000px'}) 

    , html.Div([
            html.Label('stan:', style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='dropdown-stan',
                options=[],
                multi=True,
                value=[],
                style={'width': '95%'}    
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'width': '1000px'}) 

    , html.Div([
            html.Label('liczba drzwi:', style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='dropdown-liczba-drzwi',
                options=[],
                multi=True,
                value=[],
                style={'width': '95%'}     
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'width': '1000px'}) 

    , html.Div([
            html.Label('wyposazenie:', style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='dropdown-wyposazenie',
                options=[],
                multi=True,
                value=[],
                style={'width': '95%'}     
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'width': '1000px'}) 



    ,html.Br()
    
    ,html.Button('Refresh Display', id='refresh-display-btn', n_clicks=0)
    ,dcc.Graph(id='3d-scatter-plot')
    
    ,dcc.Store(id='data-store', data={'random_data': []})
    ,html.Div(id='dummy-output', style={'display': 'none'})
])

# upload csv callback
###@app.callback(
###    Output('data-store', 'data'),
###    Input('upload-data', 'contents'),
###    State('upload-data', 'filename')
###)

###
# download csv file callback 
#--------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('download-link', 'href'),
    Input('data-store', 'data')
)
def update_download_link(stored_data):
    if stored_data:
        df = pd.DataFrame(stored_data['random_data'])
        if len(df)==0:
            return dash.no_update
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_b64 = base64.b64encode(csv_string.encode()).decode()  # Encodes the CSV string to base64
        href = f'data:text/csv;base64,{csv_b64}'  # Creates a dynamic href to download the CSV
        return href
    return dash.no_update


def decoded_to_df(decoded):
    columns=decoded.decode('utf-8').split('\r\n')[0].split(',') # this works well
    data=[]
    for l in decoded.decode('utf-8').split('\r\n')[1:-1]:
        row=l.split(',')
        data.append(row)
    df=pd.DataFrame(data,columns=columns)
    
    return clean_df(df)

# generate callback 
#--------------------------------------------------------------------------------------------------------------------------------
def update_store(contents, filename): # function to handle csv uploaded by the user 
    dash_logger.info(f'updating store ! ')
    if contents is not None:
        try:
            if 'csv' in filename:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df=decoded_to_df(decoded)
                dash_logger.info(f'uploaded df stats are {df.shape} {df.columns}')
                return df 
            else:
                raise ValueError("File type not supported")
        except Exception as e:
            dash_logger.info(f'uh oh there was an errore {e}')
            raise dash.exceptions.PreventUpdate from e
    return None

@app.callback(
    [Output('data-store', 'data')
     , Output('error-message', 'children')
     ,Output('dropdown-marka', 'options')
     ,Output('dropdown-model', 'options')
     ,Output('dropdown-skrzynia-biegow', 'options')   # STEP 2  -> add output for new df column here
     ,Output('dropdown-stan', 'options')   
     ,Output('dropdown-liczba-drzwi', 'options')   
     ,Output('dropdown-wyposazenie','options')

     ]
    ,[Input('generate-data-btn', 'n_clicks')
      ,Input('upload-data', 'contents')          # upload csv 
      ]
    ,[State('input-box-search-url', 'value')
      ,State('upload-data', 'filename')          # upload csv 
      ]
    ,prevent_initial_call=True
)
def generate_data(n_clicks,contents,url,filename):
    
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    dash_logger.info(f'trigger id is {triggered_id} filename is {filename}')
    
    if triggered_id == 'upload-data':
        dash_logger.info('data uploaded ! ')
        df= update_store(contents,filename)
        #return dash.no_update, dash.no_update, dash.no_update,dash.no_update,dash.no_update, dash.no_update
        #return {'random_data': df.to_dict('records')}, 'Data uploaded', dash.no_update,dash.no_update,dash.no_update, dash.no_update, dash.no_update
    if triggered_id=='generate-data-btn':
        # if url not like otomoto 
        if 'https://www.otomoto.pl' not in url:
            return dash.no_update, 'url not supported', dash.no_update,dash.no_update,dash.no_update, dash.no_update, dash.no_update
        
        dash_logger.info(f'generate data clicked ! with url {url}')
        df=get_df(url=url)
        
    
    if True:
        marka_vals=df['marka_pojazdu'].unique()
        marka_options=[{'label': x, 'value': x} for x in marka_vals]
        model_vals=df['model_pojazdu'].unique()
        model_options=[{'label': x, 'value': x} for x in model_vals]
        # step 3 -> add options for new df column here  
        stan_vals = df['stan'].unique()  
        stan_options = [{'label': x, 'value': x} for x in stan_vals]  

        skrzynia_biegow_vals=df['skrzynia_biegow'].unique()
        skrzynia_biegow_options=[{'label': x, 'value': x} for x in skrzynia_biegow_vals]
        
        liczba_drzwi_vals = df['liczba_drzwi'].unique()  
        liczba_drzwi_options = [{'label': str(x), 'value': x} for x in liczba_drzwi_vals]  

        wyposazenie_vals = unique_elements(df,'wyposazenie')  
        wyposazenie_options = [{'label': str(x), 'value': x} for x in wyposazenie_vals] 
        
#        return {'random_data': df.to_dict('records')}, 'Data generated',marka_options,model_options,skrzynia_biegow_options,stan_options, liczba_drzwi_options  
        return {'random_data': df.to_dict('records')}, 'Data generated',marka_options,model_options,skrzynia_biegow_options,stan_options, liczba_drzwi_options  ,wyposazenie_options


    return dash.no_update, dash.no_update, dash.no_update,dash.no_update,dash.no_update, dash.no_update, dash.no_update

# refresh callback 
#--------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('3d-scatter-plot', 'figure')
    ,[Input('refresh-display-btn', 'n_clicks')
     ,Input('3d-scatter-plot', 'clickData')
      ]
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
     ,State('dropdown-marka', 'value')
     ,State('dropdown-model', 'value')
     ,State('dropdown-skrzynia-biegow', 'value') # STEP 4 -> add state for new df column here
     ,State('dropdown-stan', 'value')  
     ,State('dropdown-liczba-drzwi', 'value')  
     ,State('dropdown-wyposazenie', 'value')  

      ]
    ,prevent_initial_call=True
)
def display_data(n_clicks,clickData, data, input_przebieg_from,input_przebieg_to,input_rok_produkcji_from,input_rok_produkcji_to
                 ,input_moc_from,input_moc_to,input_cena_from,input_cena_to,dropdown_marka,dropdown_model,dropdown_skrzynia
                 ,dropdown_stan,dropdown_liczba_drzwi,dropdown_wyposazenie
                 , col_mapping_d={'X':'przebieg','Y':'cena','Z':'rok_produkcji','COLOR':'moc'}):
    dash_logger.info(f'refresh display clicked')
    dash_logger.info(f' dropdown marka is {dropdown_marka}')
    ctx=dash.callback_context

    
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    dash_logger.info(f'refresh button clicked {input_id}')
    filters_d={'przebieg': [ [input_przebieg_from,input_przebieg_to], lambda_between] 
               ,'rok_produkcji': [ [input_rok_produkcji_from,input_rok_produkcji_to], lambda_between]
               ,'moc': [ [input_moc_from,input_moc_to], lambda_between]
               ,'cena': [ [input_cena_from,input_cena_to], lambda_between]
               ,'marka_pojazdu': [dropdown_marka, lambda_in]
               ,'model_pojazdu': [dropdown_model, lambda_in]
               ,'skrzynia_biegow':[dropdown_skrzynia, lambda_in] 
               ,'stan': [dropdown_stan, lambda_in]  
               ,'liczba_drzwi': [dropdown_liczba_drzwi, lambda_in]  
               ,'wyposazenie': [dropdown_wyposazenie, lambda_in_lst] 

               # STEP 5 -> add filter for new df column here
               }
    dash_logger.info(f'filters_d {filters_d}')
    
    if clickData is not None and input_id!='refresh-display-btn':
        point_idx = clickData['points'][0]['pointNumber']
        dash_logger.info(f'you clicked the scatter ! {point_idx} ')
        tmp_df=filter_df(pd.DataFrame(data['random_data']),filters_d)
        dash_logger.info(f'shape of df after filtering is {tmp_df.shape}')
        webbrowser.open_new(tmp_df.iloc[point_idx]['url'])
        
    
    if n_clicks > 0:
        df = pd.DataFrame(data['random_data'])
        # Check if data is empty
        if df.empty:
            return dash.no_update
        fig = make_fig(df,col_mapping_d,filters_d )
        return fig
    return dash.no_update

# Run the app

# Initialize the Dash app

if __name__ == '__main__':
    #app.run_server(debug=True, port=8051)
    app.run_server()



