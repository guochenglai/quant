import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys
import torch
from datetime import datetime

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.finrl_client import FinRLClient

class TestFinRLClient(unittest.TestCase):
    """Test cases for FinRLClient class, focusing on the train_model method."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a FinRLClient instance with test directories
        self.client = FinRLClient()
        
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_train_model(self):
       symbol = "AAPL"
       start_date = (datetime.now() - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
       end_date = datetime.now().strftime('%Y-%m-%d')
       self.client.train_model(symbol=symbol, start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    unittest.main()
