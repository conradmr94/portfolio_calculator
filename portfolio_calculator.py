import os
import pandas as pd
import requests
import math
import kagglehub as kh
from my_secrets import POLYGON_API_TOKEN
from datetime import datetime, timedelta
from tqdm import tqdm

def get_most_recent_trading_day(date):
    while True:
        if date.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
            date -= timedelta(days=1)
        else:
            test_api_url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/{date.strftime('%Y-%m-%d')}/{date.strftime('%Y-%m-%d')}?apiKey={POLYGON_API_TOKEN}"
            response = requests.get(test_api_url).json()
            if 'results' in response and len(response['results']) > 0:
                break
            else:
                date -= timedelta(days=1)
    return date

def redistribute_residuals(dataframe, portfolio_size):
    # Calculate the total allocated amount and the residual funds
    dataframe['Allocated Amount'] = dataframe['Number of Shares to Buy'] * dataframe['Stock Price']
    total_allocated = dataframe['Allocated Amount'].sum()
    residual_funds = portfolio_size - total_allocated

    # Sort stocks by the smallest fractional gap to their next share
    dataframe['Fractional Gap'] = (portfolio_size / len(dataframe) % dataframe['Stock Price']) / dataframe['Stock Price']
    sorted_df = dataframe.sort_values(by='Fractional Gap', ascending=False)

    # Distribute residual funds proportionally to fractional gaps
    for index, row in sorted_df.iterrows():
        if residual_funds <= 0:
            break

        price = row['Stock Price']
        if residual_funds >= price:
            dataframe.at[index, 'Number of Shares to Buy'] += 1
            residual_funds -= price

    return dataframe


def main():
    path = kh.dataset_download("andrewmvd/sp-500-stocks")
    stocks = pd.read_csv(path + "/sp500_companies.csv")['Symbol']

    cols = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
    data_rows = []

    today = datetime.today()
    trading_date = get_most_recent_trading_day(today)
    trading_date_str = trading_date.strftime('%Y-%m-%d')
    timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    stock_data_filename = f'stock_data_{trading_date_str}.csv'

    # Check if the file already exists
    if os.path.exists(stock_data_filename):
        print(f"File {stock_data_filename} already exists. Skipping API calls.")
        final_dataframe = pd.read_csv(stock_data_filename)
    else:
        print(f"Getting data for {trading_date_str}")

        for symbol in tqdm(stocks, desc="Processing Stocks"):
            api_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{trading_date_str}/{trading_date_str}?apiKey={POLYGON_API_TOKEN}"
            response = requests.get(api_url).json()
            if 'results' in response and len(response['results']) > 0:
                price = response['results'][0]['c']
                market_cap = price * response['results'][0]['v']
                data_rows.append({
                    'Ticker': symbol,
                    'Stock Price': price,
                    'Market Capitalization': market_cap,
                    'Number of Shares to Buy': 'N/A'
                })

        final_dataframe = pd.DataFrame(data_rows, columns=cols)
        final_dataframe.to_csv(stock_data_filename, index=False)
        print(f"Data saved to {stock_data_filename}")

    portfolio_size = input("Enter the value of your portfolio: ")
    try:
        portfolio_size = float(portfolio_size)
    except ValueError:
        print("Invalid input! Please enter a numeric value.")
        return
    
    # Check if the portfolio size is sufficient to buy at least one share of each stock
    min_required_portfolio = final_dataframe['Stock Price'].min() * len(final_dataframe.index)
    if portfolio_size < min_required_portfolio:
        print(f"Your portfolio size of ${portfolio_size:,.2f} is too small to buy at least one share of each stock.")
        return

    position_size = portfolio_size / len(final_dataframe.index)

    # Calculate initial number of shares and total allocation
    final_dataframe['Number of Shares to Buy'] = final_dataframe['Stock Price'].apply(lambda x: math.floor(position_size / x))

    # Redistribute residual funds for better equal weighting
    final_dataframe = redistribute_residuals(final_dataframe, portfolio_size)

    # Compute the total value of the portfolio
    final_dataframe['Total Value'] = final_dataframe['Number of Shares to Buy'] * final_dataframe['Stock Price']
    total_portfolio_value = final_dataframe['Total Value'].sum()
    print(f"The total value of the portfolio is: ${total_portfolio_value:,.2f}")

    output_filename = f'recommended_positions_{timestamp_str}.csv'
    final_dataframe.to_csv(output_filename, index=False)
    print(f"Recommended positions saved to {output_filename}")

if __name__ == "__main__":
    main()
