from flask import Flask, render_template, request, jsonify, send_file, session
from io import BytesIO
import requests
from datetime import datetime
from portfolio_calculator import calculate_portfolio_distribution, get_most_recent_trading_day, fetch_stock_data
import kagglehub as kh
from my_secrets import POLYGON_API_TOKEN, APP_SECRET

app = Flask(__name__)
app.secret_key = APP_SECRET

def is_valid_ticker(ticker):
    """Check if a stock ticker exists using the Polygon API."""
    ticker = ticker.upper()
    api_url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={POLYGON_API_TOKEN}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if "results" in data and "ticker" in data["results"]:
            return True  # Valid ticker
    return False  # Invalid ticker

@app.route('/')
def home():
    """Render the home page and ensure session['stock_symbols'] is initialized."""
    session['stock_symbols'] = []  # Ensure session has the stock list
    session.modified = True
    return render_template('home.html', selected_stocks=session['stock_symbols'])

@app.route('/select_stock', methods=['POST'])
def select_stock():
    """Handles selecting stocks and stores them in session after validation."""
    data = request.get_json()
    stock_symbol = data.get("stock_symbol").upper()

    if 'stock_symbols' not in session:
        session['stock_symbols'] = []  # Initialize if missing

    if stock_symbol in session['stock_symbols']:
        return jsonify({"error": "Stock already selected.", "selected_stocks": session['stock_symbols']}), 400

    if not is_valid_ticker(stock_symbol):
        return jsonify({"error": "Invalid stock ticker. Please enter a valid symbol."}), 400

    session['stock_symbols'].append(stock_symbol)
    session.modified = True  # Ensure session updates persist

    return jsonify({"selected_stocks": session['stock_symbols']})

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    """Handles removing a stock from the session."""
    data = request.get_json()
    stock_symbol = data.get("stock_symbol")

    if 'stock_symbols' in session and stock_symbol in session['stock_symbols']:
        session['stock_symbols'].remove(stock_symbol)
        session.modified = True  # Ensure session updates persist

    return jsonify({"selected_stocks": session['stock_symbols']})

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        portfolio_size = float(request.form['portfolio_size'])
    except ValueError:
        return jsonify({'error': 'Invalid portfolio size. Please enter a numeric value.'}), 400

    trading_date = get_most_recent_trading_day()
    trading_date_str = trading_date.strftime('%Y-%m-%d')

    stock_symbols = session.get('stock_symbols', [])
    if not stock_symbols:
        return render_template('home.html', error="Please select at least one stock!", selected_stocks=stock_symbols)

    stock_data = fetch_stock_data(stock_symbols, trading_date, POLYGON_API_TOKEN)

    min_required = len(stock_data) * stock_data['Stock Price'].max()
    if portfolio_size < min_required:
        error_msg = (
            f"Your portfolio size is too small. You must enter at least "
            f"${min_required:,.2f} to buy one share of every stock."
        )
        return render_template('home.html', error=error_msg, selected_stocks=stock_symbols)

    portfolio = calculate_portfolio_distribution(portfolio_size, stock_data, POLYGON_API_TOKEN)
    columns = portfolio.columns.tolist()
    rows = portfolio.values.tolist()

    print(portfolio['Allocated Amount'].sum())

    return render_template(
        'recommend.html',
        columns=columns,
        rows=rows,
        csv_data=portfolio.to_csv(index=False)
    )

@app.route('/download', methods=['POST'])
def download():
    csv_data = request.form['csv_data']
    buffer = BytesIO(csv_data.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='recommended_positions.csv', mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
