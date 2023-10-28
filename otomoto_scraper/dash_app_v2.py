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
    logging.info(f' df columns after cleaning are {df.columns}')
    return df 



def make_fig(df,col_mapping_d,filters_d):
    for k,v in filters_d.items():
        fun=v[1] 
        vals=v[0]
        if vals !=[]: # not filtering if nothing was chosen so all data from dccs are displayed by default 
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
     ,Output('dropdown-model', 'options')
     ,Output('dropdown-skrzynia-biegow', 'options')   # STEP 2  -> add output for new df column here
     ,Output('dropdown-stan', 'options')   
     ,Output('dropdown-liczba-drzwi', 'options')   

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
        model_vals=df['model_pojazdu'].unique()
        model_options=[{'label': x, 'value': x} for x in model_vals]
        # step 3 -> add options for new df column here  
        stan_vals = df['stan'].unique()  
        stan_options = [{'label': x, 'value': x} for x in stan_vals]  

        skrzynia_biegow_vals=df['skrzynia_biegow'].unique()
        ofertskrzynia_biegow_options=[{'label': x, 'value': x} for x in skrzynia_biegow_vals]
        
        liczba_drzwi_vals = df['liczba_drzwi'].unique()  
        liczba_drzwi_options = [{'label': str(x), 'value': x} for x in liczba_drzwi_vals]  

        
        return {'random_data': df.to_dict('records')}, 'Data generated',marka_options,model_options,ofertskrzynia_biegow_options,stan_options, liczba_drzwi_options  

    return dash.no_update, dash.no_update, dash.no_update,dash.no_update,dash.no_update, dash.no_update


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
     ,State('dropdown-marka', 'value')
     ,State('dropdown-model', 'value')
     ,State('dropdown-skrzynia-biegow', 'value') # STEP 4 -> add state for new df column here
     ,State('dropdown-stan', 'value')  
     ,State('dropdown-liczba-drzwi', 'value')  

      ]
    ,prevent_initial_call=True
)
def display_data(n_clicks, data, input_przebieg_from,input_przebieg_to,input_rok_produkcji_from,input_rok_produkcji_to
                 ,input_moc_from,input_moc_to,input_cena_from,input_cena_to,dropdown_marka,dropdown_model,dropdown_skrzynia
                 ,dropdown_stan,dropdown_liczba_drzwi
                 , col_mapping_d={'X':'przebieg','Y':'cena','Z':'rok_produkcji','COLOR':'moc'}):
    logging.info(f'refresh display clicked')
    logging.info(f' dropdown marka is {dropdown_marka}')
    ctx=dash.callback_context
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    logging.info(f'refresh button clicked {input_id}')
    filters_d={'przebieg': [ [input_przebieg_from,input_przebieg_to], lambda_between] 
               ,'rok_produkcji': [ [input_rok_produkcji_from,input_rok_produkcji_to], lambda_between]
               ,'moc': [ [input_moc_from,input_moc_to], lambda_between]
               ,'cena': [ [input_cena_from,input_cena_to], lambda_between]
               ,'marka_pojazdu': [dropdown_marka, lambda_in]
               ,'model_pojazdu': [dropdown_model, lambda_in]
               ,'skrzynia_biegow':[dropdown_skrzynia, lambda_in] 
               ,'stan': [dropdown_stan, lambda_in]  
               ,'liczba_drzwi': [dropdown_liczba_drzwi, lambda_in]  

               # STEP 5 -> add filter for new df column here
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

