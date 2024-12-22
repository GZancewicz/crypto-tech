import dash
from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
import requests

# Fetch Bitcoin price data
def fetch_bitcoin_data():
    url = 'https://api.coindesk.com/v1/bpi/historical/close.json?start=2020-01-01&end=2023-01-01'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(list(data['bpi'].items()), columns=['Date', 'Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Initialize the Dash app
app = dash.Dash(__name__)

# Fetch data
df = fetch_bitcoin_data()

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Bitcoin Price History'),

    dcc.Graph(
        id='bitcoin-price-graph',
        figure={
            'data': [
                go.Scatter(
                    x=df['Date'],
                    y=df['Price'],
                    mode='lines',
                    name='Bitcoin Price'
                )
            ],
            'layout': go.Layout(
                title='Bitcoin Price Over the Last 3 Years',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Price (USD)'},
            )
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)