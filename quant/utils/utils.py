import pandas as pd
from futu import *
import requests
import yfinance as yf
from .logging_config import setup_logger
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
import os

# Set up logger
logger = setup_logger('utils')

def get_spy500_symbols():
    """
    Fetch the list of S&P 500 symbols from Wikipedia
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, verify=False)
    tables = pd.read_html(response.text)
    sp500_table = tables[0]
    logger.info(f"Fetched {len(sp500_table)} symbols from S&P 500")
    return sp500_table['Symbol'].tolist()
