import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import webbrowser
import logging 
import numpy as np 
import unidecode 
logging.basicConfig(level=logging.DEBUG,filemode='w'
                    ,format='%(asctime)s - %(levelname)s - %(message)s'
                    ,filename='./logs/good_plotly.log')

logging.info('test')

app = dash.Dash(__name__) # making app global scope 

def make_random_df():
    df=pd.DataFrame({'przebieg':np.random.randint(0,5,5)
                    ,'price':np.random.randint(0,5,5)
                    ,'moc':np.random.randint(0,5,5)})
    df=pd.read_csv('./data/oo.csv',sep='\t',infer_datetime_format=True,index_col=0)
    # save original types
    
    
    # unidecode df columns 
    clean_string= lambda s: s.strip().replace(' ','_').lower()
    df.columns=[clean_string(unidecode.unidecode(x)) for x in df.columns]
    dtypes=df.dtypes
    # unidecode values in df 
    for c in df.columns:
        # column type 
        col_type=dtypes[c]
        if col_type=='object':
            df[c]=[unidecode.unidecode(str(x)) for x in df[c]]
    # cast to original types 

    
    return df 






def make_scatter(df):
    logging.info(f'making scatter plot')
    fig = px.scatter_3d(df, x=df['przebieg'], y=df['price'], z=df['moc'] )
    return fig 

def submit_button_function(przebieg_from, przebieg_to,moc_from,moc_to,rok_produkcji_from
                           ,rok_produkcji_to,dcc_inputs ):
    # Regenerate the data
    logging.info(f'submit_button_function  clicked')
    df = make_random_df()
    # log df columns 
    logging.info(f'df columns {df.columns}')
    logging.info(f'dcc inputs {dcc_inputs}') # why  [[True, True]] ?? 
    logging.info(f'df shape before  filter {df.shape}')
    logging.info(f'make submit button {przebieg_from} {przebieg_to} ')
    try:
        df = df[df['przebieg'].between(przebieg_from, przebieg_to)]               
        df=df[df['moc'].between(moc_from,moc_to)]
        df=df[df['rok_produkcji'].between(rok_produkcji_from,rok_produkcji_to)]
    except Exception as e:
        logging.error(f"Error during filtering: {e}")
    
    logging.info(f'df shape after filter {df.shape}')                             # THIS DOESNT GET LOGGED 
    # Create a new scatter plot figure

    # filter df further based on dcc_inputs 
    # {'stan': ['test', 'Uzywane'], 'Zarejestrowany w Polsce': ['Tak', 'nan']}
    for col,values in dcc_inputs.items():
        logging.info(f'filtering on {col} {values}')
        df = df[df[col].isin(values)]
        
    fig = make_scatter(df)
    
    return fig

def register_callbacks():
    logging.info('register callbacks')
    @app.callback(
        Output('graph', 'figure'),  # Only update the graph's figure
        [Input('submit-button', 'n_clicks')],
        [State('input-box-przebieg-from', 'value')
         ,State('input-box-przebieg-to', 'value')
         ,State('input-box-moc-from', 'value')
         ,State('input-box-moc-to', 'value')
         ,State('input-box-rok_produkcji-from', 'value')
         ,State('input-box-rok_produkcji-to', 'value')
         ,State('dcc-input-stan', 'value')
         ,State('dcc-input-zarejestrowany_w_polsce', 'value')
         ]
    )
    def main_callback(n_clicks,input_przebieg_from,input_przebieg_to
                      ,input_moc_from,input_moc_to,input_rok_produkcji_from,input_rok_produkcji_to
                      ,input_dcc_stan,input_dcc_zarejestrowany):
        logging.info('main callback')
        ctx=dash.callback_context
        
        if not ctx.triggered:
            logging.info('not triggered')
            return dash.no_update
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        logging.info(f'callback input_id {input_id}')
        if input_id=='submit-button':
            try:
                przebieg_from = int(input_przebieg_from)
                przebieg_to = int(input_przebieg_to)
                moc_from=int(input_moc_from)
                moc_to=int(input_moc_to)
                rok_produkcji_from=int(input_rok_produkcji_from)
                rok_produkcji_to=int(input_rok_produkcji_to)
                dcc_inputs={'stan':input_dcc_stan
                            ,'zarejestrowany_w_polsce':input_dcc_zarejestrowany
                            }
            except:
                logging.info(f'''couldnt convert inputs przebieg from: {input_przebieg_from} przebieg to: {input_przebieg_to}
                             moc from: {input_moc_from} moc to: {input_moc_to}
                             ''')
                przebieg_from=0
                przebieg_to=99999999
            new_fig = submit_button_function(przebieg_from,przebieg_to,moc_from,moc_to,rok_produkcji_from,rok_produkcji_to,dcc_inputs)  # Get the new figure
        else:
            new_fig = dash.no_update
        
        logging.info(f'input_id={input_id}')
        return new_fig
            
            
    # makes dcc format type of options_d from df data 
def get_options_d_from_df(df = None,column='Bezwypadkowy'):
    if df is None :
        df=pd.read_csv('./data/oo.csv',sep='\t',infer_datetime_format=True,index_col=0)
    # get distinct values from df on column 
    l=df[column].unique()
    # cast to ascii 
    l=[str(x) for x in l]
    # build dcc format options_d 
    options_d=[ 
               {'label': f'{x}', 'value': f'{x}'} for x in l
               ]
    logging.info(f'options_d {options_d}')
    values=[v for v in l]
    return options_d , values 
        
#d=get_options_d_from_df()
#print(d)
#exit(1)
            
            
df=make_random_df()


fig=make_scatter(df)
app.layout = html.Div([
html.Label('Przebieg from:', style={'marginRight': '10px'})
,dcc.Input(id='input-box-przebieg-from', type='text', value='0')
,html.Label('Przebieg to:', style={'marginRight': '10px'})
,dcc.Input(id='input-box-przebieg-to', type='text', value='99999999')

,html.Br()
,html.Label('Moc from: ')
,dcc.Input(id='input-box-moc-from', type='text', value='0')
,html.Label('Moc to: ')
,dcc.Input(id='input-box-moc-to', type='text', value='99999999')

,html.Br()
,html.Label('Rok produkcji from: ')
,dcc.Input(id='input-box-rok_produkcji-from', type='text', value='69')
,html.Label('Rok produkcji to: ')
,dcc.Input(id='input-box-rok_produkcji-to', type='text', value='2137')
,html.Br()

,html.Div([
html.Label('Stan:', style={'marginRight': '10px'})
,dcc.Checklist(
        id='dcc-input-stan',
        options=get_options_d_from_df(df=df,column='stan')[0],
        value=get_options_d_from_df(df=df,column='stan')[1]
        ,style={'display': 'flex'}             # Use flexbox to layout child elements in a row
        ,labelStyle={'margin-right': '20px'}    # Add some right margin to each option for spacing
    )
],style={'display': 'flex'})


,html.Div([
html.Label('zarejestrowany_w_polsce:', style={'marginRight': '10px'})
,dcc.Checklist(
        id='dcc-input-zarejestrowany_w_polsce',
        options=get_options_d_from_df(df=df,column='zarejestrowany_w_polsce')[0],
        value=get_options_d_from_df(df=df,column='zarejestrowany_w_polsce')[1]
        ,style={'display': 'flex'}             # Use flexbox to layout child elements in a row
        ,labelStyle={'margin-right': '20px'}    # Add some right margin to each option for spacing
    )
],style={'display': 'flex'})

,html.Button(id="submit-button",children='Refresh',n_clicks=0,style={'fontSize': 18, 'marginLeft': '10px'} )
,dcc.Graph(id="graph", figure=fig)
,html.Div(id='dummy-output')  # Adding a dummy output div

])
register_callbacks()
app.run_server(debug=True,use_reloader=True, dev_tools_ui=False,port=8051)