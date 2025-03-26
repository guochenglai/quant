import pandas as pd
from futu import *
import requests
import yfinance as yf
from .logging_config import setup_logger
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
import os

# Set up logger
logger = setup_logger('utils')

def download_data(start_date, end_date, ticker_list):
    """
    Download stock data using Yahoo Downloader.
    
    Args:
        start_date (str): Start date for historical data
        end_date (str): End date for historical data
        ticker_list (list): List of ticker symbols
        
    Returns:
        pandas.DataFrame: Downloaded stock data
    """
    try:
        logger.info(f"Downloading data for {ticker_list} from {start_date} to {end_date}")
        df = YahooDownloader(
            start_date=start_date,
            end_date=end_date,
            ticker_list=ticker_list
        ).fetch_data()
        logger.info(f"Successfully downloaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error downloading data: {str(e)}")
        raise

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
