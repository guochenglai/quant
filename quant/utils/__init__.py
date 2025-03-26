import pandas as pd
from futu import *
import requests
import yfinance as yf
from .logging_config import setup_logger
import os

# Set up logger
logger = setup_logger('utils')


def get_spy500_tickers():
    """
    Fetch the list of S&P 500 tickers from Wikipedia
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, verify=False)
    tables = pd.read_html(response.text)
    sp500_table = tables[0]
    logger.info(f"Fetched {len(sp500_table)} tickers from S&P 500")
    return sp500_table['Symbol'].tolist()


def fetch_real_time_data(ticker):
    logger.info(f"Fetching real-time data for {ticker}")
    try:
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=33333)  
        ret, data = quote_ctx.get_market_snapshot(['US.AAPL'])
        quote_ctx.close()
        if ret == RET_OK:
            logger.info(f"Real-time data for {ticker}: {data}")
            return data
    except Exception as e:
        logger.error(f"Error fetching real-time data: {str(e)}")
        return None
    
def fetch_stock_data(ticker, start_date=None, end_date=None, period="1y"):
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

def save_data(data, ticker):
    """Save data to CSV file"""
    try:
        file_name = f"{ticker}.csv"
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_dir, "../data", file_name)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        data.to_csv(file_path)
        logger.info(f"Data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        raise