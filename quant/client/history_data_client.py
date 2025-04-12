import pandas as pd
from futu import *
import requests, logging
import yfinance as yf
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
from quant.constants import *

class HistoryDataClient:
    """
    A client for fetching historical data.
    """
    def __init__(self, logger=None):
        """
        Initialize the History Data client.
        
        Args:
            logger (logging.Logger): Logger instance. If None, uses a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)

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
            self.logger.info(f"Downloading data for {ticker_list} from {start_date} to {end_date}")
            df = YahooDownloader(
                start_date=start_date,
                end_date=end_date,
                ticker_list=ticker_list
            ).fetch_data()
            self.logger.info(f"Successfully downloaded data with shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error downloading data: {str(e)}")
    
    def batch_fetch_data(self, symbols, start_date, end_date):
        """
        Fetches historical data for multiple symbols between start_date and end_date.

        :param symbols: List of symbols for which to fetch historical data.
        :param start_date: The start date for the historical data.
        :param end_date: The end date for the historical data.
        :return: Historical data for the specified symbols and date range.
        """
        try:
            self.logger.info(f"Downloading data for {symbols} from {start_date} to {end_date}")
            df = YahooDownloader(
                start_date=start_date,
                end_date=end_date,
                ticker_list=symbols
            ).fetch_data()
            self.logger.info(f"Successfully downloaded data with shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error downloading data: {str(e)}")
            raise
    
    def save_data(self, df, symbol):
        """
        Saves the fetched data to a specified file path.

        :param df: The DataFrame containing the data to save.
        :param file_path: The path where the data should be saved.
        """
        try:
            file_path = os.path.join(
                project_root_dir,
                '../data',
                f"{symbol}.csv"
            )

            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Existing file {file_path} removed.")

            df.to_csv(file_path, index=False)
            self.logger.info(f"Data saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            raise