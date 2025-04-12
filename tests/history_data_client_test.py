import unittest
import sys
import os
from datetime import datetime, timedelta
from quant.logger import configure_logger

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.history_data_client import HistoryDataClient

class TestHistoryDataClient(unittest.TestCase):
    """Test cases for HistoryDataClient class"""
    
    def setUp(self):
        """Set up test fixtures."""
        # Configure test-specific logger
        self.logger = configure_logger(
            name='history_data_test',
            is_test=True,
            test_file_name='history_data_client_test'
        )
        
        # Initialize client with logger
        self.client = HistoryDataClient(logger=self.logger)
        self.logger.info("HistoryDataClientTest setup complete")
        
        # Set up test parameters
        self.symbol = "AAPL"
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    def test_fetch_data(self):
        """Test fetching historical data for a single symbol."""
        self.logger.info(f"Testing fetch_data for {self.symbol}")
        df = self.client.fetch_data(self.symbol, self.start_date, self.end_date)
        self.assertIsNotNone(df)
        self.assertTrue(len(df) > 0)
        self.logger.info(f"Successfully fetched {len(df)} rows of data")
    
    def test_batch_fetch_data(self):
        """Test fetching historical data for multiple symbols."""
        symbols = ["AAPL", "MSFT", "GOOG"]
        self.logger.info(f"Testing batch_fetch_data for {symbols}")
        df = self.client.batch_fetch_data(symbols, self.start_date, self.end_date)
        self.assertIsNotNone(df)
        self.assertTrue(len(df) > 0)
        self.logger.info(f"Successfully fetched {len(df)} rows of data for multiple symbols")
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("HistoryDataClientTest teardown complete")

if __name__ == "__main__":
    unittest.main()
