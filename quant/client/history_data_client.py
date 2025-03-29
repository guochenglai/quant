import pandas as pd
from futu import *
import requests
import yfinance as yf
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
from quant.utils.logging_config import setup_logger
logger = setup_logger('quant.history_data_client')

class HistoryDataClient:
    """
    A client for fetching historical data.
    """

    def __init__(self, data_source):
        """
        Initializes the HistoryDataClient with a data source.

        :param data_source: The source from which to fetch historical data.
        """
        self.data_source = data_source

    def fetch_data(self, symbol, start_date, end_date):
        """
        Fetches historical data for a given symbol between start_date and end_date.

        :param symbol: The symbol for which to fetch historical data.
        :param start_date: The start date for the historical data.
        :param end_date: The end date for the historical data.
        :return: Historical data for the specified symbol and date range.
        """
        try:
            ticker_list = [symbol]
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