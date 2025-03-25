# This script is used for downloading S&P 500 stock data incrementally.

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from utils.logging_config import setup_logger
from utils import get_spy500_tickers
logger = setup_logger('quant.fetch_sp500_data')
logger.info("Starting SP500 incremental data fetching process")


def fetch_and_save_stock_data(ticker, start_date=None, end_date=None):
    """Fetch stock data incrementally and save to CSV"""
    try:
        logger.info(f"Fetching data for {ticker}")

        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_dir, "stock_data", f"{ticker}.csv")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            last_date = pd.to_datetime(existing_data.index[-1]) + timedelta(days=1)
            incremental_start_date = last_date.strftime('%Y-%m-%d')
            logger.info(f"Existing data found for {ticker}, fetching from {incremental_start_date}")
        else:
            existing_data = pd.DataFrame()
            incremental_start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
            logger.info(f"No existing data found for {ticker}, fetching from {incremental_start_date}")

        new_data = yf.download(ticker, start=incremental_start_date, end=datetime.now().strftime('%Y-%m-%d'))

        if new_data.empty:
            logger.warning(f"No new data fetched for {ticker}")
            return

        combined_data = pd.concat([existing_data, new_data]).drop_duplicates()
        combined_data.to_csv(file_path)
        logger.info(f"Data saved for {ticker} at {file_path}")
    except Exception as e:
        logger.error(f"Error fetching/saving data for {ticker}: {str(e)}")

if __name__ == "__main__":
    tickers = get_spy500_tickers()
    logger.info(f"Fetched {len(tickers)} tickers from SP500")

    for ticker in tickers:
        fetch_and_save_stock_data(ticker)

    logger.info("SP500 data fetching process completed")
