import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys # Add this line

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from datetime import datetime
from quant.logger import configure_logger

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.finrl_client import FinRLClient

class TestFinRLClient(unittest.TestCase):
    """Test cases for FinRLClient class, focusing on the train_model method."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Configure test-specific logger
        self.logger = configure_logger(
            name='finrl_test',
            is_test=True,
            test_file_name='finrl_client_test'
        )
        # Create a FinRLClient instance with test directories and logger
        self.client = FinRLClient(logger=self.logger)
        self.logger.info("FinRLClientTest setup complete")
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("FinRLClientTest teardown complete")
    
    def test_train_model(self):
       self.logger.info("Testing train_model method")
       symbols = ["AAPL", "MSFT", "GOOGL"]
       start_date = (datetime.now() - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
       end_date = datetime.now().strftime('%Y-%m-%d')
       self.client.train_model(symbols=symbols, start_date=start_date, end_date=end_date)
       self.logger.info("Train model test completed")

if __name__ == "__main__":
    unittest.main()
