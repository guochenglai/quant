import unittest
import os, json
from quant.client.paper_trading_client import PaperTradingClient
from quant.logger import configure_logger
import sys 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class PaperTradingClientTest(unittest.TestCase):
    
    def setUp(self):
        # Configure test-specific logger
        self.logger = configure_logger(
            name='paper_trading_test',
            is_test=True,
            test_file_name='paper_trading_client_test'
        )
        # Initialize client with logger
        self.paper_trading_client = PaperTradingClient(logger=self.logger)
        self.logger.info("PaperTradingClientTest setup complete")
    
    def test_get_account_info(self):
        """Test fetching account information."""
        account_info = self.paper_trading_client.get_account_info()
        
        self.logger.info("Getting account info...")
        # Check if the account info is not None and contains expected keys
        self.assertIsNotNone(account_info)
        
    
    def test_is_tradeable(self):
        """Test checking if a symbol is tradable."""
        symbol = "AAPL" 
        self.logger.info(f"Checking if {symbol} is tradeable...")
        is_tradeable = self.paper_trading_client.is_tradeable(symbol)


    def test_get_positions(self):
        """Test fetching positions."""
        self.logger.info("Getting positions...")
        symbol = "AAPL"
        positions, portfolio = self.paper_trading_client.get_positions(symbol)
        
        # Check if the positions are not None and is a list
        self.assertIsNotNone(positions)
        self.assertIsNotNone(portfolio)


    def test_get_all_orders(self):
        """Test fetching all orders."""
        orders = self.paper_trading_client.get_all_orders()

        self.logger.info("Getting all orders...")
        # Check if the orders are not None and is a list
        self.assertIsNotNone(orders)


    # def test_buy_market_order(self):
    #     """Test placing a market buy order."""
    #     symbol = "MSFT"
    #     quantity = 1
        
    #     self.logger.info(f"Placing market buy order for {quantity} shares of {symbol}...")
        
    #     order = self.paper_trading_client.buy_market_order(symbol, quantity)

    #     # Check if the order is not None and contains expected keys
    #     self.assertIsNotNone(order)

    #     # Print the order for debugging purposes
    #     self.logger.info(f"=================== Buy Market Order ==================== \n: {json.dumps(order, indent=4, default=str)}")

    # def test_sell_market_order(self):
    #     """Test placing a market sell order."""
    #     symbol = "AAPL"
    #     quantity = 1
        
    #     self.logger.info(f"Placing market sell order for {quantity} shares of {symbol}...")

    #     order = self.paper_trading_client.sell_market_order(symbol, quantity)

    #     # Check if the order is not None and contains expected keys
    #     self.assertIsNotNone(order)

    #     # Print the order for debugging purposes
    #     self.logger.info(f"=================== Sell Market Order ==================== \n: {json.dumps(order, indent=4, default=str)}")

    def tearDown(self):
        """Clean up after tests."""
        self.logger.info("PaperTradingClientTest teardown complete")
        pass

if __name__ == '__main__':
    unittest.main()
