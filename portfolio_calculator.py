import math
import pandas as pd
import requests
from datetime import datetime, timedelta

def get_most_recent_trading_day():
    """Get the most recent trading day (not a weekend or holiday)."""
    date = datetime.today()
    while True:
        if date.weekday() in [5, 6]:
            date -= timedelta(days=1)
        else:
            return date

def fetch_stock_data(stock_symbols, trading_date, api_token):
    """Fetch stock data (price and market cap) from the Polygon API."""
    trading_date_str = trading_date.strftime('%Y-%m-%d')
    stock_data = []

    for symbol in stock_symbols:
        api_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{trading_date_str}/{trading_date_str}?apiKey={api_token}"
        response = requests.get(api_url).json()
        if 'results' in response and len(response['results']) > 0:
            price = response['results'][0]['c']
            volume = response['results'][0]['v']
            market_cap = price * volume
            stock_data.append({
                'Ticker': symbol,
                'Stock Price': price,
                'Market Capitalization': market_cap
            })

    return pd.DataFrame(stock_data)

def redistribute_residuals(dataframe, portfolio_size):
    """Redistribute residual funds for better equal weighting."""
    dataframe['Allocated Amount'] = dataframe['Number of Shares to Buy'] * dataframe['Stock Price']
    residual_funds = portfolio_size - dataframe['Allocated Amount'].sum()

    dataframe['Fractional Gap'] = (portfolio_size / len(dataframe) % dataframe['Stock Price']) / dataframe['Stock Price']
    sorted_df = dataframe.sort_values(by='Fractional Gap', ascending=False)

    for index, row in sorted_df.iterrows():
        if residual_funds <= 0:
            break
        price = row['Stock Price']
        if residual_funds >= price:
            dataframe.at[index, 'Number of Shares to Buy'] += 1
            residual_funds -= price

    return dataframe

def calculate_portfolio_distribution(portfolio_size, stock_data, api_token):
    """Calculate the portfolio distribution based on equal weight strategy."""
    position_size = portfolio_size / len(stock_data)

    stock_data['Number of Shares to Buy'] = stock_data['Stock Price'].apply(lambda x: math.floor(position_size / x))
    redistribute_residuals(stock_data, portfolio_size)

    stock_data['Total Value'] = stock_data['Number of Shares to Buy'] * stock_data['Stock Price']
    return stock_data

