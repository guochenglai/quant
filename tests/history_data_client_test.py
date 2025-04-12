import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys
import torch
from datetime import datetime

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.history_data_client import HistoryDataClient
from quant.utils.utils import get_spy500_symbols

class TestHostoryDataClient(unittest.TestCase):
    """Test cases for HistoryDataClient class, focusing on get history data of stocks."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = HistoryDataClient()
        
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_fetch_and_save_history_data(self):
        symbols = get_spy500_symbols()
        for symbol in symbols:
            start_date = (datetime.now() - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = self.client.fetch_data(symbol=symbol, start_date=start_date, end_date=end_date)
            if df is None:
                print(f"No data found for {symbol}")
                continue
            self.client.save_data(df, symbol=symbol)

if __name__ == "__main__":
    unittest.main()
