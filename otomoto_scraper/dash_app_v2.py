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
def get_df(fp='./data/oo.csv',sep='\t'):
    logging.info(' getting df ')
    df=pd.read_csv(fp,sep=sep,infer_datetime_format=True,index_col=0)   
    logging.info(f'got df of shape {df.shape}')
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
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([html.Br()
                       
                       
    ,html.Label('Przebieg from:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-przebieg-from', type='text', value='0')
    ,html.Label('Przebieg to:', style={'marginRight': '10px'})
    ,dcc.Input(id='input-box-przebieg-to', type='text', value='99999999')
    
    ,html.Br()
    ,html.Button('Generate Data', id='generate-data-btn', n_clicks=0)
    ,html.Button('Refresh Display', id='refresh-display-btn', n_clicks=0)
    ,dcc.Graph(id='3d-scatter-plot')
    ,html.Div('No data available', id='error-message', style={'color': 'red'})
    ,dcc.Store(id='data-store', data={'random_data': []})
])

# Callback to generate random data and update data generation status
@app.callback(
    [Output('data-store', 'data'), Output('error-message', 'children')],
    [Input('generate-data-btn', 'n_clicks')],
    prevent_initial_call=True
)
def generate_data(n_clicks):
    if n_clicks > 0:
        X = np.random.randint(0, 100, 10)
        Y = np.random.randint(0, 100, 10)
        Z = np.random.randint(0, 100, 10)
        df = pd.DataFrame({'X': X, 'Y': Y, 'Z': Z})
        df=get_df()
        return {'random_data': df.to_dict('records')}, 'Data generated'
    return dash.no_update, dash.no_update

# Callback to display the data in a 3D scatter plot or display an error message if no data
@app.callback(
    Output('3d-scatter-plot', 'figure')
    ,[Input('refresh-display-btn', 'n_clicks')]
    ,[
      State('data-store', 'data')
     ,State('input-box-przebieg-from', 'value')
     ,State('input-box-przebieg-to', 'value')
      ]
    ,prevent_initial_call=True
)
def display_data(n_clicks, data,input_przebieg_from,input_przebieg_to
                 , col_mapping_d={'X':'przebieg','Y':'price','Z':'rok_produkcji','COLOR':'moc'}):
    logging.info(f'refresh display clicked')
    ctx=dash.callback_context
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    logging.info(f'refresh button clicked {input_id}')
    filters_d={'przebieg': [ [input_przebieg_from,input_przebieg_to], lambda_between] }
    logging.info(f'filters_d {filters_d}')
    
    if n_clicks > 0:
        df = pd.DataFrame(data['random_data'])
        
        # Check if data is empty
        if df.empty:
            return dash.no_update
#        fig = px.scatter_3d(df, x=df[col_mapping_d['X']], y=df[col_mapping_d['Y']], z=df[col_mapping_d['Z']],color=df[col_mapping_d['COLOR']] )
        fig = make_fig(df,col_mapping_d,filters_d )
        return fig
    return dash.no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)



# OLD WAY OF SCATTER 
        ###fig2 = {
        ###    "data": [{
        ###        "type": "scatter3d",
        ###        "x": df[col_mapping_d['X']],
        ###        "y": df[col_mapping_d['Y']],
        ###        "z": df[col_mapping_d['Z']],
        ###        "mode": "markers",
        ###        "marker": {
        ###            "size": 10,
        ###            "color": df[col_mapping_d['COLOR']],  # set color to Z values for variation
        ###            "colorscale": 'Viridis',
        ###            "opacity": 0.8
        ###        }
        ###    }],
        ###    "layout": {
        ###        "title": "3D Scatter Plot",
        ###        "scene": {
        ###            "xaxis": {"title": f'{col_mapping_d["X"]}'},
        ###            "yaxis": {"title": f'{col_mapping_d["Y"]}'},
        ###            "zaxis": {"title": f'{col_mapping_d["Z"]}'},
        ###        }
        ###    }
        ###}