# Import necessary libraries
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import random
import asyncio

# Create a Dash app instance
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Random Number Generator"),
    html.Button("Generate Random Number", id="generate-button", n_clicks=0),
    html.Div(id="random-number-output"),
])

# Async function to simulate some async operation
async def async_hello_world():
    print("Hello World from asyncio!")
    await asyncio.sleep(1)  # Simulate a non-blocking task

# Define the callback to update the output div
@app.callback(
    Output("random-number-output", "children"),
    [Input("generate-button", "n_clicks")]
)
def generate_random_number(n_clicks):
    if n_clicks > 0:
        # Run the async function
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_hello_world())

        random_number = random.randint(1, 100)
        return html.H2(f"Random Number: {random_number}")
    return html.H2("Click the button to generate a random number")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
