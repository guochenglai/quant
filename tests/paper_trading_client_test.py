import unittest
import os, json
from quant.client.paper_trading_clinet import PaperTradingClient

class PaperTradingClientTest(unittest.TestCase):
    
    def setUp(self):
        self.polygon_client = PaperTradingClient()

    
    def test_get_account_info(self):
        """Test fetching account information."""
        account_info = self.polygon_client.get_account_info()
        
        print(f"Getting account info...")
        # Check if the account info is not None and contains expected keys
        self.assertIsNotNone(account_info)
        
    
    def test_is_tradeable(self):
        """Test checking if a symbol is tradable."""
        symbol = "AAPL" 
        print(f"Checking if {symbol} is tradeable...")
        is_tradeable = self.polygon_client.is_tradeable(symbol)


    def test_get_positions(self):
        """Test fetching positions."""
        print(f"Getting positions...")
        symbol = "AAPL"
        positions, portfolio = self.polygon_client.get_positions(symbol)
        
        # Check if the positions are not None and is a list
        self.assertIsNotNone(positions)
        self.assertIsNotNone(portfolio)


    def test_get_all_orders(self):
        """Test fetching all orders."""
        orders = self.polygon_client.get_all_orders()

        print(f"Getting all orders...")
        # Check if the orders are not None and is a list
        self.assertIsNotNone(orders)


    def test_buy_market_order(self):
        """Test placing a market buy order."""
        symbol = "MSFT"
        quantity = 1
        
        print(f"Placing market buy order for {quantity} shares of {symbol}...")
        
        order = self.polygon_client.buy_market_order(symbol, quantity)

        # Check if the order is not None and contains expected keys
        self.assertIsNotNone(order)

        # Print the order for debugging purposes
        print(f"=================== Buy Market Order ==================== \n: {json.dumps(order, indent=4, default=str)}")

    def test_sell_market_order(self):
        """Test placing a market sell order."""
        symbol = "AAPL"
        quantity = 1
        
        print(f"Placing market sell order for {quantity} shares of {symbol}...")

        order = self.polygon_client.sell_market_order(symbol, quantity)

        # Check if the order is not None and contains expected keys
        self.assertIsNotNone(order)

        # Print the order for debugging purposes
        print(f"=================== Sell Market Order ==================== \n: {json.dumps(order, indent=4, default=str)}")

    def tearDown(self):
        """Clean up after tests."""
        pass

if __name__ == '__main__':
    unittest.main()
