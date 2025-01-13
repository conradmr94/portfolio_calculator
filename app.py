from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO
import pandas as pd
import os
from datetime import datetime
from portfolio_calculator import calculate_portfolio_distribution, get_most_recent_trading_day, fetch_stock_data
import kagglehub as kh
from my_secrets import POLYGON_API_TOKEN

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        portfolio_size = float(request.form['portfolio_size'])
    except ValueError:
        return jsonify({'error': 'Invalid portfolio size. Please enter a numeric value.'}), 400

    # Determine the most recent trading day
    trading_date = get_most_recent_trading_day()
    trading_date_str = trading_date.strftime('%Y-%m-%d')

    # Define the filename for the stock data
    stock_data_filename = f"stock_data_{trading_date_str}.csv"

    if os.path.exists(stock_data_filename):
        # Use existing stock data file
        print(f"Using existing stock data file: {stock_data_filename}")
        stock_data = pd.read_csv(stock_data_filename)
    else:
        # Download stock symbols from Kaggle
        print("Downloading S&P 500 stock data from Kaggle...")
        path = kh.dataset_download("andrewmvd/sp-500-stocks")
        stock_symbols = pd.read_csv(path + "/sp500_companies.csv")['Symbol']

        # Fetch stock data from Polygon API
        print("Fetching stock data from Polygon API...")
        stock_data = fetch_stock_data(stock_symbols, trading_date, POLYGON_API_TOKEN)

        # Save the data to a CSV file for future use
        stock_data.to_csv(stock_data_filename, index=False)
        print(f"Stock data saved to {stock_data_filename}")

    # Generate the portfolio distribution
    portfolio = calculate_portfolio_distribution(portfolio_size, stock_data, POLYGON_API_TOKEN)

    # Pass column headers and rows for table rendering
    columns = portfolio.columns.tolist()
    rows = portfolio.values.tolist()

    # Render the recommendations page
    return render_template(
        'recommend.html',
        columns=columns,
        rows=rows,
        csv_data=portfolio.to_csv(index=False)
    )

@app.route('/download', methods=['POST'])
def download():
    csv_data = request.form['csv_data']

    # Convert the CSV data back into a BytesIO object
    buffer = BytesIO(csv_data.encode('utf-8'))
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='recommended_positions.csv', mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
