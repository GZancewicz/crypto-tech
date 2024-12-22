import dash
from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
import json
from dash.dependencies import Input, Output

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

    dcc.Graph(id='bitcoin-price-graph'),

    dcc.RangeSlider(
        id='date-range-slider',
        min=0,
        max=len(df) - 1,
        value=[0, len(df) - 1],
        marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(df['Date'][::len(df)//10])},
        step=1
    )
])

# Update the graph based on the slider
@app.callback(
    Output('bitcoin-price-graph', 'figure'),
    [Input('date-range-slider', 'value')]
)
def update_graph(date_range):
    filtered_df = df.iloc[date_range[0]:date_range[1]+1]
    return {
        'data': [
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['Price'],
                mode='lines',
                name='Bitcoin Price'
            )
        ],
        'layout': go.Layout(
            title='Bitcoin Price Over the Selected Range',
            xaxis={'title': 'Date'},
            yaxis={'title': 'Price (USD)'},
        )
    }

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)