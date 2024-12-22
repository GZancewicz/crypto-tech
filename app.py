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

# Calculate technical indicators and signals
def calculate_indicators(df):
    df['SMA_10'] = df['Price'].rolling(window=10).mean()
    df['SMA_50'] = df['Price'].rolling(window=50).mean()
    delta = df['Price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Generate buy/sell signals
    df['Buy_Signal'] = ((df['SMA_10'] > df['SMA_50']) & (df['SMA_10'].shift(1) <= df['SMA_50'].shift(1))) | (df['RSI'] < 30)
    df['Sell_Signal'] = ((df['SMA_10'] < df['SMA_50']) & (df['SMA_10'].shift(1) >= df['SMA_50'].shift(1))) | (df['RSI'] > 70)
    
    return df

# Initialize the Dash app
app = dash.Dash(__name__)

# Load and process data
df = load_bitcoin_data()
df = calculate_indicators(df)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Bitcoin Price History'),

    dcc.Graph(id='bitcoin-price-graph'),
    dcc.Graph(id='sma-graph'),

    dcc.RangeSlider(
        id='date-range-slider',
        min=0,
        max=len(df) - 1,
        value=[0, len(df) - 1],
        marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(df['Date'][::len(df)//10])},
        step=1
    ),

    html.Label('Short SMA period'),
    html.Div(id='sma-value', style={'margin-top': 10}),
    dcc.Slider(
        id='sma-slider',
        min=0,
        max=100,
        value=20,  # Default short SMA period
        marks={i: str(i) for i in range(0, 101, 10)},
        step=1
    ),

    html.Label('Long SMA period'),
    html.Div(id='second-slider-value', style={'margin-top': 10}),
    dcc.Slider(
        id='second-slider',
        min=10,
        max=100,
        value=50,  # Default long SMA period
        marks={i: str(i) for i in range(10, 101, 10)},
        step=1
    )
])

# Update the graphs and display the SMA value
@app.callback(
    [Output('bitcoin-price-graph', 'figure'),
     Output('sma-graph', 'figure'),
     Output('sma-value', 'children'),
     Output('second-slider', 'min'),
     Output('second-slider-value', 'children')],
    [Input('date-range-slider', 'value'),
     Input('sma-slider', 'value'),
     Input('second-slider', 'value')]
)
def update_graphs(date_range, m, second_value):
    m = max(m, 1)  # Ensure m is at least 1
    filtered_df = df.iloc[date_range[0]:date_range[1]+1]
    filtered_df['SMA_M'] = filtered_df['Price'].rolling(window=m).mean()
    filtered_df['SMA_Long'] = filtered_df['Price'].rolling(window=second_value).mean()
    
    price_figure = {
        'data': [
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['Price'],
                mode='lines',
                name='Bitcoin Price'
            )
        ],
        'layout': go.Layout(
            title='Bitcoin Price',
            xaxis={'title': 'Date'},
            yaxis={'title': 'Price (USD)'},
        )
    }

    sma_figure = {
        'data': [
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['Price'],
                mode='lines',
                line=dict(color='lightgray'),
                name='Bitcoin Price'
            ),
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['SMA_M'],
                mode='lines',
                name=f'Short SMA {m}'
            ),
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['SMA_Long'],
                mode='lines',
                name=f'Long SMA {second_value}'
            )
        ],
        'layout': go.Layout(
            title=f'SMA Periods',
            xaxis={'title': 'Date'},
            yaxis={'title': 'SMA Value'},
        )
    }

    sma_value_text = f'Selected Short SMA Period: {m}'
    second_slider_min = m
    second_slider_value_text = f'Selected Long SMA Period: {second_value}'

    return price_figure, sma_figure, sma_value_text, second_slider_min, second_slider_value_text

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)