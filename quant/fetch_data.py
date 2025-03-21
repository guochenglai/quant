import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
from utils.logging_config import setup_logger

# Set up logger
logger = setup_logger('quant.fetch_data')
logger.info("Starting data fetching process")

def fetch_stock_data(ticker="AAPL", start_date=None, end_date=None, period="1y"):
    """
    Fetch stock data using yfinance
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        period (str): Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        pd.DataFrame: DataFrame with stock data
    """
    logger.info(f"Fetching data for {ticker} from {start_date} to {end_date} (period: {period})")
    
    try:
        if start_date and end_date:
            data = yf.download(ticker, start=start_date, end=end_date)
        else:
            data = yf.download(ticker, period=period)
        
        logger.info(f"Successfully fetched data with shape: {data.shape}")
        return data
    
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise

def save_data(data, file_name="aapl_data.csv"):
    """Save data to CSV file"""
    try:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_dir, "data", file_name)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        data.to_csv(file_path)
        logger.info(f"Data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Executing data fetching script")
    
    # Define parameters
    ticker = "AAPL"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    logger.info(f"Fetching {ticker} data from {start_date} to {end_date}")
    
    # Fetch and save data
    data = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)
    save_data(data, "aapl_data.csv")
    
    logger.info("Data fetching process completed")
