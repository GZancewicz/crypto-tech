import dash
from dash import html, dcc, dash_table
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from dash.dependencies import Input, Output
from datetime import datetime, timedelta

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
def calculate_indicators(df, short_window, long_window):
    df['SMA_Short'] = df['Price'].rolling(window=short_window).mean()
    df['SMA_Long'] = df['Price'].rolling(window=long_window).mean()
    df['Buy_Signal'] = (df['SMA_Short'] > df['SMA_Long']) & (df['SMA_Short'].shift(1) <= df['SMA_Long'].shift(1))
    df['Sell_Signal'] = (df['SMA_Short'] < df['SMA_Long']) & (df['SMA_Short'].shift(1) >= df['SMA_Long'].shift(1))
    return df

# Backtesting function
def backtest_strategy(df, short_window, long_window, initial_investment=100.0):
    df = calculate_indicators(df.copy(), short_window, long_window)
    df['Position'] = np.where(df['Buy_Signal'], 1, 0)
    df['Position'] = np.where(df['Sell_Signal'], -1, df['Position'])
    df['Position'] = df['Position'].shift(1).fillna(0)
    df['Portfolio Value'] = initial_investment * (1 + df['Price'].pct_change().fillna(0) * df['Position']).cumprod()
    return df['Portfolio Value'].iloc[-1]

# Generate random dates, M, and N values
def generate_random_dates(num_dates=100):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)
    random_dates = pd.to_datetime(np.random.choice(pd.date_range(start_date, end_date), num_dates, replace=False))
    random_m_values = np.random.randint(1, 101, size=num_dates)
    random_n_values = [np.random.randint(m, 101) for m in random_m_values]
    return pd.DataFrame({'Random Dates': random_dates, 'M': random_m_values, 'N': random_n_values})

# Initialize the Dash app
app = dash.Dash(__name__)

# Load and process data
df = load_bitcoin_data()

# Define the layout of the app
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-2', children=[
        dcc.Tab(label='BTC', value='tab-1'),
        dcc.Tab(label='BTC SMA Optimization', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])

# Callback to render the content of the selected tab
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1(children='Bitcoin Price History and Backtesting'),

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
            ),

            html.Div(id='backtest-result', style={'margin-top': 20})
        ])
    elif tab == 'tab-2':
        random_dates_df = generate_random_dates()
        return html.Div([
            html.H1(children='BTC SMA Optimization'),
            dash_table.DataTable(
                data=random_dates_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in random_dates_df.columns],
                page_size=10
            )
        ])

# Update the graphs and display the SMA value
@app.callback(
    [Output('bitcoin-price-graph', 'figure'),
     Output('sma-graph', 'figure'),
     Output('sma-value', 'children'),
     Output('second-slider', 'min'),
     Output('second-slider-value', 'children'),
     Output('backtest-result', 'children')],
    [Input('tabs', 'value'),
     Input('date-range-slider', 'value'),
     Input('sma-slider', 'value'),
     Input('second-slider', 'value')]
)
def update_graphs(tab, date_range, m, second_value):
    if tab != 'tab-1':
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    m = max(m, 1)  # Ensure m is at least 1
    filtered_df = df.iloc[date_range[0]:date_range[1]+1]
    filtered_df = calculate_indicators(filtered_df, m, second_value)
    
    buy_signals = filtered_df[filtered_df['Buy_Signal']]
    sell_signals = filtered_df[filtered_df['Sell_Signal']]
    
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
                y=filtered_df['SMA_Short'],
                mode='lines',
                name=f'Short SMA {m}'
            ),
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['SMA_Long'],
                mode='lines',
                name=f'Long SMA {second_value}'
            ),
            go.Scatter(
                x=buy_signals['Date'],
                y=buy_signals['Price'],
                mode='markers',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                name='Buy Signal'
            ),
            go.Scatter(
                x=sell_signals['Date'],
                y=sell_signals['Price'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                name='Sell Signal'
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

    # Perform backtesting
    final_portfolio_value = backtest_strategy(filtered_df, m, second_value)
    backtest_result_text = f'Final Portfolio Value: {final_portfolio_value:.2f} units'

    return price_figure, sma_figure, sma_value_text, second_slider_min, second_slider_value_text, backtest_result_text

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)