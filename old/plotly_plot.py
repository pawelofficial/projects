import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import webbrowser
import logging 
logging.basicConfig(level=logging.INFO,filemode='a',format='%(asctime)s - %(levelname)s - %(message)s'
                    ,filename='plotly.log')
logging.info('Start of program')

def load_and_filter_data(file_path = './stats_df.csv'
                         , keywords=['alfa', 'mito', 'corsa', 'fiesta']
                         , selected_columns=['cena', 'Przebieg', 'Rok produkcji', 'Moc', 'tytul']):
    df = pd.read_csv(file_path, sep='|', infer_datetime_format=True, index_col=0)
    df = df[df['tytul'].str.contains('|'.join(keywords), case=False)]
    data = df[selected_columns]
    return df, data


def create_3d_scatter(data
                      , cols = ['cena', 'Przebieg', 'Rok produkcji', 'Moc', 'tytul']
                      , extra_hover_data = ['tytul']
                      ):
    size_data = (data[cols[3]] - data[cols[3]].min()) / (data[cols[3]].max() - data[cols[3]].min()) * 100
    
    fig = px.scatter_3d(data, x=cols[0], y=cols[1], z=cols[2],
                        color=cols[3], size=size_data,
                        text=data['tytul'].apply(lambda x: ' '.join(x.split()[:2])),
                        color_continuous_scale='RdYlGn',
                        hover_data={col: True for col in cols},
                        custom_data=extra_hover_data)

    fig.update_traces(
        hovertemplate=(
            f"<b>{cols[0]}:</b> %{{x}}<br>"
            f"<b>{cols[1]}:</b> %{{y}}<br>"
            f"<b>{cols[2]}:</b> %{{z}}<br>"
            f"<b>{cols[3]}:</b> %{{marker.color}}<br>"
            f"<b>tytul:</b> %{{customdata[0]}}<extra></extra>"
        ),
        hoverinfo="x+y+z+text+name",
        marker=dict(size=10, sizemode='diameter'),
        hoverlabel=dict(
            bgcolor="rgba(240, 240, 240, 0.2)",
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
            xaxis_title=cols[0],
            yaxis_title=cols[1],
            zaxis_title=cols[2],
        ),
        coloraxis_colorbar=dict(
            title=cols[3],
            x=0,
            xanchor="left"
        )
    )
    return fig


def init_dash_app(df, fig
                  ,default_values=['Alfa Romeo','Ford Fiesta','Opel Corsa']):
    app = dash.Dash(__name__)
    unique_tytuls = df['tytul'].apply(lambda x: ' '.join(x.split()[:2])).unique()
    dropdown_options = [{'label': tytul, 'value': tytul} for tytul in unique_tytuls]

    app.layout = html.Div([
        dcc.Store(id='stored-data'),
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize': 18, 'marginLeft': '10px'}
        ),
        dcc.Dropdown(
            id='tytul-dropdown',
            options=dropdown_options,
            multi=True,
            value=[option['value'] for option in dropdown_options if option['value'] in default_values ]
        ),
        dcc.Graph(
            id='3d-scatter',
            figure=fig,
            style={'height': '100vh', 'width': '100vw'}
        ),html.Div(id='hidden-div', style={'display':'none'})
    ], style={'margin': '0', 'padding': '0'})

    return app



def handle_scatter_click(clickData, df):
    logging.info(f'3D scatter plot clicked')
    try:
        point_idx = clickData['points'][0]['pointNumber']
        logging.info(f'point_idx: {point_idx}')
        webbrowser.open(df.iloc[point_idx]['url'], new=0)
        logging.info(f'webbrowser opened {point_idx}')
    except KeyError:
        logging.error('KeyError encountered. The structure of clickData may have changed.')
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        
    
def handle_submit_button(n_clicks, dropdown_value):
    logging.info(f'Submit button clicked {n_clicks} times')
    logging.info(f'Selected values in dropdown: {dropdown_value}')


def register_callbacks(app, df, fig):
    @app.callback(
        [Output('3d-scatter', 'figure'),
         Output('hidden-div', 'children')],
        [Input('3d-scatter', 'clickData'),
         Input('submit-button', 'n_clicks')],
        [State('tytul-dropdown', 'value'),
         State('hidden-div', 'children')]
    )
        
    def display_click_data(clickData, n_clicks, dropdown_value, current_df_json):
            ctx = dash.callback_context

            if not ctx.triggered:
                return fig, df.to_json(date_format='iso', orient='split')

            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            current_df = pd.read_json(current_df_json, orient='split')

            if trigger_id == '3d-scatter' and clickData:
                handle_scatter_click(clickData, current_df)

            elif trigger_id == 'submit-button' and n_clicks:
                handle_submit_button(n_clicks, dropdown_value)
                new_df, data = load_and_filter_data(keywords=dropdown_value)
                updated_fig = create_3d_scatter(data)
                logging.info(f'updated df len ->  {len(new_df)} ')
                return updated_fig, new_df.to_json(date_format='iso', orient='split')

            return fig, df.to_json(date_format='iso', orient='split')


def main():
    file_path = './stats_df.csv'
    keywords =[] # ['alfa', 'mito', 'corsa', 'fiesta']
    selected_columns = ['cena', 'Przebieg', 'Rok produkcji', 'Moc', 'tytul']
    extra_hover_data = ['tytul']

    df, data = load_and_filter_data(file_path, keywords, selected_columns)
    fig = create_3d_scatter(data, selected_columns, extra_hover_data)
    
    app = init_dash_app(df, fig)
    register_callbacks(app, df, fig)

    app.run_server(debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
