import requests
import json

# Fetch Bitcoin price data with high, low, and close prices
def fetch_bitcoin_data():
    url = 'https://api.coindesk.com/v1/bpi/historical/ohlc.json?start=2020-01-01&end=2023-01-01'
    response = requests.get(url)
    data = response.json()
    return data

# Write data to BTC.json
def write_to_json(data, filename='BTC.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Main execution
if __name__ == '__main__':
    bitcoin_data = fetch_bitcoin_data()
    write_to_json(bitcoin_data)
