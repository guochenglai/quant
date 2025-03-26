import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import logging
import sys
import os

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.futu_client import FutuClient
from futu import OpenQuoteContext, OpenUSTradeContext, TrdEnv, OrderType, OrderSide, TimeInForce

class TestFutuClient(unittest.TestCase):
    """Test cases for FutuClient class"""
    
    def setUp(self):
        """Set up test fixtures, if any."""
        # Create a mock logger
        self.mock_logger = MagicMock(spec=logging.Logger)
        
        # Set up FutuClient with mock logger
        self.client = FutuClient(
            host="127.0.0.1", 
            port=1111, 
            trade_host="127.0.0.1", 
            trade_port=11111, 
            trade_password="test_password", 
            trd_env=TrdEnv.SIMULATE,
            logger=self.mock_logger
        )

        self.client.connect()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.client.quote_context:
            self.client.quote_context.close()
        if self.client.trade_context:
            self.client.trade_context.close()
        self.client.disconnect()

    def test_fetch_real_time_data(self):
        """Test initialization of FutuClient."""
        data = self.client.fetch_real_time_data("US.AAPL")


   