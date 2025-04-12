import unittest
import os, json
from quant.client.realtime_data_client import PolygonClient

class PolygonClientTest(unittest.TestCase):
    
    def setUp(self):
        self.polygon_client = PolygonClient()

    
    def test_get_symbol_list(self):
        """Test fetching symbol list from Polygon API."""
        symbols = self.polygon_client.get_symbol_list(market="stocks", active="true", order="asc", limit=10, sort="ticker")
        print(json.dumps(symbols, indent=4, default=str))
    
    def test_get_symbol_details(self):
        """Test fetching symbol details from Polygon API."""
        symbol = "AAPL"
        details = self.polygon_client.get_symbol_details(symbol)
        print(details)
        

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'client'):
            self.client.disconnect()

if __name__ == '__main__':
    unittest.main()
