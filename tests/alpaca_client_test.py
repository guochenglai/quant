import unittest
import os, time
from quant.client.realtime_data_client import AlPacaClient

class AlPacaClientTest(unittest.TestCase):
    
    def setUp(self):
        self.alpaca_client = AlPacaClient()

    
    def test_get_tick_list(self):
        """Test fetching tick list from Polygon API."""
        for i in range(10):
            ticks = self.alpaca_client.get_ticker_details(ticker="AAPL")
            print(ticks)
            time.sleep(1)
        

    def tearDown(self):
        """Clean up after tests."""
       pass

if __name__ == '__main__':
    unittest.main()
