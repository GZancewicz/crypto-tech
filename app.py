import dash
from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
import json

# Load Bitcoin price data from BTC.json
def load_bitcoin_data(filename='BTC.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
    # Extract date and close price
    records = [(date, values['close']) for date, values in data['bpi'].items()]
    df = pd.DataFrame(records, columns=['Date', 'Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Initialize the Dash app
app = dash.Dash(__name__)

# Load data
df = load_bitcoin_data()

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