import unittest
from datetime import datetime
import pandas as pd
import os
import sys
from quant.logger import configure_logger

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.utils.utils import get_spy500_symbols

class UtilsTest(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Configure test-specific logger
        self.logger = configure_logger(
            name='utils_test',
            is_test=True,
            test_file_name='utils_test'
        )
        self.logger.info("UtilsTest setup complete")
    
    def test_get_spy500_symbols(self):
        """Test fetching S&P 500 symbols."""
        # Test if the function returns a list
        self.logger.info("Testing get_spy500_symbols function")
        tickers = get_spy500_symbols(logger=self.logger)
        
        self.logger.info(f"S&P 500 symbols: {len(tickers)} retrieved")
        
        # Test if the list is not empty
        self.assertGreater(len(tickers), 0)
        self.logger.info(f"First 5 symbols: {tickers[:5]}")
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("UtilsTest teardown complete")

if __name__ == "__main__":
    unittest.main()