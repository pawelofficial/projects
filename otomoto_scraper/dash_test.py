# Import necessary libraries
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.Button('Generate Data', id='generate-data-btn', n_clicks=0),
    html.Button('Refresh Display', id='refresh-display-btn', n_clicks=0),
    dcc.Graph(id='3d-scatter-plot'),
    html.Div(id='error-message', style={'color': 'red'}),
    dcc.Store(id='data-store', data={'random_data': []})
])

# Callback to generate random data
@app.callback(
    Output('data-store', 'data'),
    [Input('generate-data-btn', 'n_clicks')],
    prevent_initial_call=True
)
def generate_data(n_clicks):
    if n_clicks > 0:
        X = np.random.randint(0, 100, 10)
        Y = np.random.randint(0, 100, 10)
        Z = np.random.randint(0, 100, 10)
        df = pd.DataFrame({'X': X, 'Y': Y, 'Z': Z})
        return {'random_data': df.to_dict('records')}
    return dash.no_update

# Callback to display the data in a 3D scatter plot or display an error message
@app.callback(
    Output('3d-scatter-plot', 'figure'),
    Output('error-message', 'children'),
    [Input('refresh-display-btn', 'n_clicks')],
    [State('data-store', 'data')],
    prevent_initial_call=True
)
def display_data(n_clicks, data):
    if n_clicks > 0:
        df = pd.DataFrame(data['random_data'])

        # Check if data is empty
        if df.empty:
            return dash.no_update, 'Please click "Generate Data" first before displaying.'

        fig = {
            "data": [{
                "type": "scatter3d",
                "x": df['X'],
                "y": df['Y'],
                "z": df['Z'],
                "mode": "markers",
                "marker": {
                    "size": 10,
                    "color": df['Z'],  # set color to Z values for variation
                    "colorscale": 'Viridis',
                    "opacity": 0.8
                }
            }],
            "layout": {
                "title": "3D Scatter Plot",
                "scene": {
                    "xaxis": {"title": "X"},
                    "yaxis": {"title": "Y"},
                    "zaxis": {"title": "Z"},
                }
            }
        }
        return fig, ''
    return dash.no_update, dash.no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=8051)
