import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import logging
import sys
import os
import time

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.futu_client import FutuClient
from futu import OpenQuoteContext, OpenUSTradeContext, TrdEnv, OrderType, TrdSide, TimeInForce

class TestFutuClient(unittest.TestCase):
    """Test cases for FutuClient class"""
    
    def setUp(self):
        """Set up test fixtures, if any."""
        
        # Set up FutuClient with mock logger
        self.client = FutuClient(
            host="127.0.0.1", 
            port=11111,  # Fixed port - should be 11111 to match Futu OpenD default
            trade_host="127.0.0.1", 
            trade_port=11111, 
            trade_password="test_password", 
            trd_env=TrdEnv.SIMULATE
        )

        # Try to connect with retries
        max_retries = 3
        for attempt in range(max_retries):
            if self.client.connect():
                print(f"Successfully connected on attempt {attempt + 1}")
                break
            elif attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"Failed to connect after {max_retries} attempts. Please ensure Futu OpenD is running.")
                # Don't fail the test setup, we'll check connection in the test itself
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'client'):
            self.client.disconnect()

    def test_fetch_real_time_data(self):
        """Test fetching real-time data."""
        # Verify connection was successful before proceeding
        if not self.client.quote_context:
            self.skipTest("Skipping test as connection to Futu OpenD failed. Please verify the service is running.")
        
        data = self.client.fetch_real_time_data("US.AAPL")
        print(data)

if __name__ == '__main__':
    unittest.main()