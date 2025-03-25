import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
from utils.logging_config import setup_logger
from utils import fetch_stock_data, save_data

# Set up logger
logger = setup_logger('quant.fetch_data')
logger.info("Starting data fetching process")

if __name__ == "__main__":
    logger.info("Executing data fetching script")
    
    # Define parameters
    ticker = "AAPL"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    logger.info(f"Fetching {ticker} data from {start_date} to {end_date}")
    
    # Fetch and save data
    data = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)
    save_data(data, ticker)
    
    logger.info("Data fetching process completed")
