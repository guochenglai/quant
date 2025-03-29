import unittest
import os
from quant.client.realtime_data_client import PolygonClient

class TestRealtimeDataClient(unittest.TestCase):
    
    def setUp(self):
        self.polygon_client = PolygonClient()

    
    def test_get_tick_list(self):
        """Test fetching tick list from Polygon API."""
        ticks = self.polygon_client.get_tick_list(market="stocks", active="true", order="asc", limit=10, sort="ticker")
        print(ticks)
        

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'client'):
            self.client.disconnect()

if __name__ == '__main__':
    unittest.main()
