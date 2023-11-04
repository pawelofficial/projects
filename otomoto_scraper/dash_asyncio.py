# Import necessary libraries
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import random
import asyncio
import httpx
import logging 

logging.basicConfig(level=logging.INFO, filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename='./logs/dash_asyncio.log')

logger = logging.getLogger('dash_asyncio')
logger.info('this is dash_asyncio ')

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Create a Dash app instance

with open('./data/links.txt', 'r') as f:
    urls = f.read().splitlines()
URLS=urls[:5]


async def fetch(url):
    headers= {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url,headers=headers)
        return response

async def fetch_all(urls, delay_interval=50, delay_seconds=1):
    tasks = []
    for i, url in enumerate(urls):
        tasks.append(fetch(url))
        # Introduce a delay every `delay_interval` requests
        if (i + 1) % delay_interval == 0:
            await asyncio.sleep(delay_seconds)
    responses = await asyncio.gather(*tasks)
    logger.info(f'Number of urls: {responses}')
    return responses

async def parallel_fetch(urls=None):
    if urls is None: 
        with open('./data/links.txt', 'r') as f:
            urls = f.read().splitlines()
    urls=urls[:5]
    logger.info(f'Number of urls: {len(urls)}')
    #df= asyncio.run(fetch_all(urls))
    df=fetch_all(urls)
    return df 



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
        asyncio.run(async_hello_world())      # works fine 
        #df= parallel_fetch()          # doesnt work -> coroutine error 
        df= asyncio.run(fetch_all(URLS))     
        logger.info(f'df is {df}')
        random_number = random.randint(1, 100)
        return html.H2(f"Random Number: {random_number}")
    return html.H2("Click the button to generate a random number")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
