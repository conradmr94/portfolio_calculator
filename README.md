# Portfolio Distribution Calculator

## Current Status
This project is a work in progress. At this time it does the following:
1. Ask the user for the desired value of their portfolio
2. Give user option to select from a list of stocks or enter their own tickers manually
3. Recommend an equally-weighted portfolio 
4. Display portfolio distribution
5. Allow user to download distribution as a CSV

## Goals
The end-state of this project is the following:
1. Allow user to select indices, ETFs, etc.
2. Allow user to choose investment strategy
3. Ask the user for the desired value of their portfolio
4. Recommend a portfolio distribution based on the selected stocks and chosen strategy

## Setup
1. Clone this repo: `git clone git@github.com:conradmr94/portfolio_calculator.git`
2. Create **Python 3.12** virtual environment in the same directory where you cloned the repo: `python3.12 -m venv .venv`
3. Activate the virtual environment:
    - On macOS and Linux: `source .venv/bin/activate`
    - On Windows: `.venv\Scripts\activate`
4. Create `my_secrets.py` in the root directory with:
    ```
    POLYGON_API_TOKEN = <your_polygon.io_api_token>
    APP_SECRET = <flask_app_secret>
    ```
4. Install the required dependencies: `pip install -r requirements.txt`

## Running the Program
Inside your virtual environment, run: `flask run`, which will open a browser window with the webapp.
