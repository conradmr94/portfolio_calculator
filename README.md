# Portfolio Distribution Calculator

## Current Status
This project is a work in progress. At this time it does the following:
1. Fetch the current S&P 500 index tickers
2. Ask the user for the desired value of their portfolio
3. Recommend an equally-weighted portfolio based on the portfolio value that tracks the S&P500

## Goals
The end-state of this project is the following:
1. Allow user to select stocks, indices, ETFs, etc.
2. ALlow user to choose investment strategy
3. Ask the user for the desired value of their portfolio
4. Recommend a portfolio distribution based on the selected stocks and chosen strategy

## Setup
1. Clone this repo: `git clone git@github.com:conradmr94/portfolio_calculator.git`
2. Create **Python 3.12** virtual environment in the same directory where you cloned the repo: `python3.12 -m venv .venv`
3. Activate the virtual environment:
    - On macOS and Linux: `source .venv/bin/activate`
    - On Windows: `.venv\Scripts\activate`
4. Install the required dependencies: `pip install -r requirements.txt`

## Running the Program
Inside your virtual environment, run: `python3 portfolio_calculator.py` and follow the terminal prompts. 