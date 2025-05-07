import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import sys 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import time
from quant.logger import configure_logger

from quant.client.futu_client import FutuClient
from futu import OpenQuoteContext, OpenUSTradeContext, TrdEnv, OrderType, TrdSide, TimeInForce

class TestFutuClient(unittest.TestCase):
    """Test cases for FutuClient class"""
    
    def setUp(self):
        """Set up test fixtures, if any."""
        # Configure test-specific logger
        self.logger = configure_logger(
            name='futu_test',
            is_test=True,
            test_file_name='futu_client_test'
        )
        
        # Set up FutuClient with logger
        self.client = FutuClient(
            host="127.0.0.1", 
            port=11111,  # Fixed port - should be 11111 to match Futu OpenD default
            trade_host="127.0.0.1", 
            trade_port=11111, 
            trade_password="test_password", 
            trd_env=TrdEnv.SIMULATE,
            logger=self.logger
        )

        # Try to connect with retries
        max_retries = 3
        for attempt in range(max_retries):
            if self.client.connect():
                self.logger.info(f"Successfully connected on attempt {attempt + 1}")
                break
            elif attempt < max_retries - 1:
                self.logger.info(f"Connection attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)
            else:
                self.logger.error(f"Failed to connect after {max_retries} attempts. Please ensure Futu OpenD is running.")
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'client'):
            self.client.disconnect()
        self.logger.info("FutuClientTest teardown complete")

    def test_fetch_real_time_data(self):
        """Test fetching real-time data."""
        # Verify connection was successful before proceeding
        if not self.client.quote_context:
            self.skipTest("Skipping test as connection to Futu OpenD failed. Please verify the service is running.")
        
        self.logger.info("Testing fetch_real_time_data function")
        data = self.client.fetch_real_time_data("US.AAPL")
        self.logger.info(f"Received data: {data}")
        self.assertIsNotNone(data)

if __name__ == '__main__':
    unittest.main()