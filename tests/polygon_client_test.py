import unittest
import os
from quant.logger import configure_logger
import sys 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from quant.client.realtime_data_client import PolygonClient

class PolygonClientTest(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Configure test-specific logger
        self.logger = configure_logger(
            name='polygon_test',
            is_test=True,
            test_file_name='polygon_client_test'
        )
        
        # Initialize client with logger
        self.polygon_client = PolygonClient(logger=self.logger)
        self.logger.info("PolygonClientTest setup complete")
    
    def test_get_symbol_list(self):
        """Test fetching symbol list from Polygon API."""
        self.logger.info("Testing get_symbol_list function")
        symbols = self.polygon_client.get_symbol_list(market="stocks", active="true", order="asc", limit=10, sort="ticker")
        
        self.assertIsNotNone(symbols)
        self.logger.info(f"Retrieved {len(symbols)} symbols from Polygon API")
    
    # def test_get_symbol_details(self):
    #     """Test fetching symbol details from Polygon API."""
    #     symbol = "AAPL"
    #     self.logger.info(f"Testing get_symbol_details for {symbol}")
        
    #     details = self.polygon_client.get_symbol_details(symbol)
    #     self.assertIsNotNone(details)
    #     self.logger.info(f"Successfully retrieved details for {symbol}")
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("PolygonClientTest teardown complete")

if __name__ == '__main__':
    unittest.main()
