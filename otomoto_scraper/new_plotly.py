import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import webbrowser
import logging 
logging.basicConfig(level=logging.INFO,filemode='w'
                    ,format='%(asctime)s - %(levelname)s - %(message)s'
                    ,filename='./logs/new_plotly.log')

app = dash.Dash(__name__) # making app global scope 


# loads data 
def load_data():
    df = pd.read_csv('./data/oo.csv', sep='\t'
                     , infer_datetime_format=True, index_col=0)
    return df


df= load_data()


# returns view of df filtered
def filter_df(df, col, fun, val,cols=[], **kwargs):
    def contains(df,col,s):
        msk=df[col].str.contains(s,case=False)
        return msk 
    def gt_or_lt(df, col, val, gt):
        if gt:
            msk=df[col].astype(float) >= val
        else:
            msk=df[col].astype(float) < val
        return msk
    funs_d = {
        'contains': contains,
        'gt_or_lt':  gt_or_lt
    }
    msk = funs_d[fun](df, col, val, **kwargs)
    if cols==[]:
        cols=df.columns
    return df[cols][msk]
    
# makes hover template string 
def make_hover_template(hover_cols : list ,dims : dict,df):
    hovertemplate=""""""
    for k, v in dims.items():
        if k=='color':
            hovertemplate+=f"<b>{ dims['color'] }:</b> %{{marker.color}}<br>"
        else:
            hovertemplate += f'<b>{v}:</b> %{{{k}}}<br>'   
    for c in hover_cols:
        hovertemplate+=f'<b>{c}:</b> %{{customdata[{hover_cols.index(c)}]}}<br>'
    return hovertemplate

# creates 3d scatter plot 
def create_3d_scatter(df
                      ,dims={'x':'Przebieg'
                             ,'y':'price'
                             ,'z':'Rok produkcji'
                             ,'color':'Moc'
                             }
                            ,hover_cols=['title','Generacja','Pojemność skokowa','Rodzaj paliwa','Skrzynia biegów']
                            ,size_col='Pojemność skokowa'):

    fig = px.scatter_3d(df
                        , x=df[dims['x']]
                        , y=df[dims['y']]
                        , z=df[dims['z']]
                        ,color=df[dims['color']]
                        #,size=10
                        ,text=df['title'].apply(lambda x: ' '.join(x.split()[:2]))
                        ,color_continuous_scale='RdYlGn'
                        ,hover_data={col: True for col in hover_cols}
                        ,custom_data=hover_cols)

    hovertemplate=make_hover_template(hover_cols,dims=dims,df=df)
    fig.update_traces(
        hovertemplate=(hovertemplate),
        hoverinfo="x+y+z+text+name",
        marker=dict(size=10, sizemode='diameter'),
        hoverlabel=dict(
            #bgcolor="rgba(240, 240, 240, 0)",
            bordercolor="black",
            font=dict(
                family="Arial, sans-serif",
                size=16,
                color="black"
            )
        )
    )
    fig.update_layout(
        scene=dict(
            xaxis_title=dims['x'],
            yaxis_title=dims['y'],
            zaxis_title=dims['z'],
        ),
        coloraxis_colorbar=dict(
            title=dims['color'],
            x=0,
            xanchor="left"
        )
    )
    return fig 


def handle_scatter_click_function(clickData):
    # Logic for handling scatter plot click
    if clickData:
        try:
            point_idx = clickData['points'][0]['pointNumber']
            logging.info(f'point_idx: {point_idx}')
            webbrowser.open(df.iloc[point_idx]['url'], new=0)
            logging.info(f'webbrowser opened {point_idx}')
        except KeyError:
            logging.error('KeyError encountered. The structure of clickData may have changed.')
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
    return "Scatter clicked"  # or some other message/output

def handle_submit_button_function(n_clicks):
    global df 
    # Logic for handling submit button click
    logging.info(f'Submit button clicked {n_clicks} times')
    # truncate df here ?
    msk=df['Przebieg'].astype(float)> 50000
    df=df[msk]
    return f'Button clicked {n_clicks} times'


def register_callbacks():
    @app.callback(
        [Output('dummy-output', 'children'),
        Output('3d-scatter', 'figure')],  # Add this output
        [Input('submit-button', 'n_clicks'),
         Input('3d-scatter', 'clickData')]
    )
    def main_callback(n_clicks, clickData):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Not triggered yet", create_3d_scatter(df) 
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'submit-button':
                message = handle_submit_button_function(n_clicks)
                return message, create_3d_scatter(df)
            elif input_id == '3d-scatter':
                message = handle_scatter_click_function(clickData)
                return message, create_3d_scatter(df) 
            
    return fig 
    
    
if __name__ == '__main__':
    fig=create_3d_scatter(df)
    app.layout = html.Div([
    dcc.RangeSlider(
    id='przebieg-slider',
    min=df['Przebieg'].min(),
    max=df['Przebieg'].max(),
    step=1000,  # or whatever granularity you want
    marks={str(przebieg): str(przebieg) for przebieg in range(df['Przebieg'].min(), df['Przebieg'].max(), 10000)},
    value=[df['Przebieg'].min(), df['Przebieg'].max()]
    )
    ,html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize': 18, 'marginLeft': '10px'}
        )
    ,dcc.Dropdown(
            id='car-dropdown',
            options=[],
            multi=True,
            value=[] # [option['value'] for option in dropdown_options if option['value'] in default_values ]
        )
    ,dcc.Graph(
            id='3d-scatter',
            figure=fig,
            style={'height': '100vh', 'width': '100vw'}
            )
        ,html.Div(id='dummy-output', style={'display': 'none'})
    ])

    register_callbacks()
    app.run_server(debug=False,use_reloader=True, dev_tools_ui=False,port=8051)
#    create_3d_scatter(df)
#    app = dash.Dash(__name__)
    
#    df2=filter_df(df=df, col='Przebieg', fun='gt_or_lt', val=50000, gt=True,cols=[])
#    # min, max przebieg 
#    print(df2)
##@    print(f(df,'Przebieg',100,gt=False))
#@    print(df)