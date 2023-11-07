import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Random Data Generator"

# Define the layout of the app
app.layout = html.Div([
    html.H1("Random Data Generator"),
    html.Button("Generate Random Data", id="generate-button"),
    html.Div(id="list-container")
])

# Define callback to update list data
@app.callback(
    Output("list-container", "children"),
    [Input("generate-button", "n_clicks")]
)
def update_list(n_clicks):
    if n_clicks is None:
        # No clicks yet, so don't display anything
        return None
    
    # Generate random data
    data = {
        'A': np.random.randint(0, 100, 10),
        'B': np.random.randint(0, 100, 10),
        'C': np.random.randint(0, 100, 10)
    }
    
    # Convert the data to a list of HTML elements
    lists = []
    for col, vals in data.items():
        lists.append(html.H3(f"Column {col}"))
        lists.append(html.Ul([
            html.Li(html.A(str(val), href="https://www.google.com", target="_blank")) for val in vals
        ]))
    
    # Return the lists
    return lists

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
