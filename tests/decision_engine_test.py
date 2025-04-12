import unittest
import sys
import os
import numpy as np
from unittest.mock import patch, MagicMock
from quant.logger import configure_logger

# Add parent directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.client.decision_engine import DecisionEngine

class TestDecisionEngine(unittest.TestCase):
    """Test cases for DecisionEngine class"""
    
    def setUp(self):
        """Set up test fixtures."""
        # Configure test-specific logger
        self.logger = configure_logger(
            name='decision_engine_test',
            is_test=True,
            test_file_name='decision_engine_test'
        )
        
        # Initialize client with logger
        self.decision_engine = DecisionEngine(logger=self.logger)
        self.logger.info("DecisionEngineTest setup complete")
        
    
    @patch('numpy.random.random')
    def test_buy_action(self, mock_random):
        """Test that the engine returns a BUY action when random value is high."""
        # Set up the mock to return a value that will trigger a BUY action
        mock_random.return_value = 0.8  # This will give random_value = 0.6 after transformation
        
        symbol = "AAPL"
        market_data = {"price": 150.0, "volume": 1000000}
        current_position = 5
        
        self.logger.info(f"Testing BUY action with {symbol}, position: {current_position}")
        action, confidence, target_qty = self.decision_engine.get_action(symbol, market_data, current_position)
        
        self.assertEqual("BUY", action)
        self.assertGreater(confidence, 0.5)  # Should have high confidence
        self.assertGreater(target_qty, current_position)  # Should increase position
        self.logger.info(f"BUY test result: action={action}, confidence={confidence:.2f}, target_qty={target_qty}")
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("DecisionEngineTest teardown complete")

if __name__ == "__main__":
    unittest.main()
