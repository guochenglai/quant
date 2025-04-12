import pandas as pd
from futu import *
import requests, logging
import yfinance as yf
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
import os

def get_spy500_symbols(logger=None):
    """
    Fetch the list of S&P 500 symbols from Wikipedia
    
    Args:
        logger (logging.Logger): Logger instance. If None, uses a default logger.
    
    Returns:
        list: List of S&P 500 symbols
    """
    logger = logger or logging.getLogger(__name__)
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        logger.info(f"Fetching S&P 500 symbols from {url}")
        response = requests.get(url, verify=False)
        tables = pd.read_html(response.text)
        sp500_table = tables[0]
        logger.info(f"Fetched {len(sp500_table)} symbols from S&P 500")
        return sp500_table['Symbol'].tolist()
    except Exception as e:
        logger.error(f"Error fetching S&P 500 symbols: {str(e)}")
        return []
