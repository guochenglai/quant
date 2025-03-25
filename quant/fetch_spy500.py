# This script is used for downloading S&P 500 stock data incrementally.

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from utils.logging_config import setup_logger
from utils import get_spy500_tickers, fetch_stock_data, save_data
logger = setup_logger('quant.fetch_sp500_data')
logger.info("Starting SP500 incremental data fetching process")


def fetch_and_save_stock_data(ticker, start_date=None, end_date=None):
    """Fetch stock data incrementally and save to CSV"""
    try:
        logger.info(f"Fetching data for {ticker}")
        data = fetch_stock_data(ticker, start_date, end_date)
        
        save_data(data, ticker)

    except Exception as e:
        logger.error(f"Error fetching/saving data for {ticker}: {str(e)}")

if __name__ == "__main__":
    tickers = get_spy500_tickers()
    logger.info(f"Fetched {len(tickers)} tickers from SP500")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    for ticker in tickers:
        fetch_and_save_stock_data(ticker, start_date, end_date)

    logger.info("SP500 data fetching process completed")
