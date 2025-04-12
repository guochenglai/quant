import unittest
import os, time
from quant.client.realtime_data_client import AlPacaClient
from quant.logger import configure_logger

class AlPacaClientTest(unittest.TestCase):
    
    def setUp(self):
        # Configure test-specific logger
        self.logger = configure_logger(
            name='alpaca_test',
            is_test=True,
            test_file_name='alpaca_client_test'
        )
        # Initialize client with logger
        self.alpaca_client = AlPacaClient(logger=self.logger)
        self.logger.info("AlPacaClientTest setup complete")
    
    def test_get_symbol_list(self):
        """Test fetching symbol list from Alpaca API."""
        for i in range(10):
            symbols = self.alpaca_client.get_symbol_details(symbol="AAPL")
            self.logger.info(f"Received data for AAPL: {symbols}")
            time.sleep(1)
        

    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("AlPacaClientTest teardown complete")

if __name__ == '__main__':
    unittest.main()
