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
            host="test_host", 
            port=12345, 
            trade_host="test_trade_host", 
            trade_port=54321, 
            trade_password="test_password", 
            trd_env=TrdEnv.SIMULATE,
            logger=self.mock_logger
        )

    def test_init(self):
        """Test initialization of FutuClient."""
        self.assertEqual(self.client.host, "test_host")
        self.assertEqual(self.client.port, 12345)
        self.assertEqual(self.client.trade_host, "test_trade_host")
        self.assertEqual(self.client.trade_port, 54321)
        self.assertEqual(self.client.trade_password, "test_password")
        self.assertEqual(self.client.trd_env, TrdEnv.SIMULATE)
        self.assertEqual(self.client.logger, self.mock_logger)
        self.assertIsNone(self.client.quote_context)
        self.assertIsNone(self.client.trade_context)

    @patch('quant.client.futu_client.OpenQuoteContext')
    @patch('quant.client.futu_client.OpenUSTradeContext')
    def test_connect_success(self, mock_trade, mock_quote):
        """Test successful connection to Futu servers."""
        # Set up mock returns
        mock_quote_instance = MagicMock()
        mock_quote.return_value = mock_quote_instance
        
        mock_trade_instance = MagicMock()
        mock_trade.return_value = mock_trade_instance
        
        # Call connect
        result = self.client.connect()
        
        # Verify the result and method calls
        self.assertTrue(result)
        mock_quote.assert_called_once_with(host="test_host", port=12345)
        mock_trade.assert_called_once_with(
            host="test_trade_host", 
            port=54321, 
            password="test_password", 
            trd_env=TrdEnv.SIMULATE
        )
        self.mock_logger.info.assert_called_once_with("Successfully connected to Futu servers for US market")

    @patch('quant.client.futu_client.OpenQuoteContext')
    def test_connect_without_trade_password(self, mock_quote):
        """Test connection without trade password."""
        # Create a client without trade password
        client = FutuClient(host="test_host", port=12345, logger=self.mock_logger)
        
        # Set up mock returns
        mock_quote_instance = MagicMock()
        mock_quote.return_value = mock_quote_instance
        
        # Call connect
        result = client.connect()
        
        # Verify the result and method calls
        self.assertTrue(result)
        mock_quote.assert_called_once_with(host="test_host", port=12345)
        self.mock_logger.info.assert_called_once()

    @patch('quant.client.futu_client.OpenQuoteContext')
    def test_connect_failure(self, mock_quote):
        """Test failed connection to Futu servers."""
        # Set up mock to raise an exception
        mock_quote.side_effect = Exception("Connection error")
        
        # Call connect
        result = self.client.connect()
        
        # Verify the result and method calls
        self.assertFalse(result)
        self.mock_logger.error.assert_called_once()

    def test_disconnect(self):
        """Test disconnection from Futu servers."""
        # Set up mock quote and trade contexts
        self.client.quote_context = MagicMock()
        self.client.trade_context = MagicMock()
        
        # Call disconnect
        self.client.disconnect()
        
        # Verify method calls
        self.client.quote_context.close.assert_called_once()
        self.client.trade_context.close.assert_called_once()
        self.mock_logger.info.assert_called_once_with("Disconnected from Futu servers")

    def test_fetch_real_time_data_no_context(self):
        """Test fetching data without an initialized context."""
        # Ensure no quote context
        self.client.quote_context = None
        
        # Call fetch_real_time_data
        result = self.client.fetch_real_time_data("US.AAPL")
        
        # Verify results
        self.assertTrue(result.empty)
        self.mock_logger.error.assert_called_once()

    def test_fetch_real_time_data_quote(self):
        """Test fetching quote data."""
        # Set up mock quote context
        self.client.quote_context = MagicMock()
        
        # Configure mocks for subscription and data fetching
        self.client.quote_context.subscribe.return_value = (0, "Success")
        
        # Mock DataFrame for the return data
        mock_data = pd.DataFrame({'symbol': ['US.AAPL'], 'last_price': [150.0]})
        self.client.quote_context.get_stock_quote.return_value = (0, mock_data)
        
        # Call fetch_real_time_data
        result = self.client.fetch_real_time_data("US.AAPL")
        
        # Verify results
        self.assertEqual(result.iloc[0]['last_price'], 150.0)
        self.client.quote_context.subscribe.assert_called_once_with("US.AAPL", ["QUOTE"])
        self.client.quote_context.get_stock_quote.assert_called_once_with("US.AAPL")

    def test_fetch_real_time_data_order_book(self):
        """Test fetching order book data."""
        # Set up mock quote context
        self.client.quote_context = MagicMock()
        
        # Configure mocks for subscription and data fetching
        self.client.quote_context.subscribe.return_value = (0, "Success")
        
        # Mock DataFrame for the return data
        mock_data = pd.DataFrame({'bid': [[150.0, 149.9]], 'ask': [[150.1, 150.2]]})
        self.client.quote_context.get_order_book.return_value = (0, mock_data)
        
        # Call fetch_real_time_data
        result = self.client.fetch_real_time_data("US.AAPL", ["ORDER_BOOK"])
        
        # Verify results
        self.assertEqual(result.iloc[0]['bid'][0], 150.0)
        self.client.quote_context.subscribe.assert_called_once_with("US.AAPL", ["ORDER_BOOK"])
        self.client.quote_context.get_order_book.assert_called_once_with("US.AAPL")

    def test_fetch_real_time_data_kline(self):
        """Test fetching K-line data."""
        # Set up mock quote context
        self.client.quote_context = MagicMock()
        
        # Configure mocks for subscription and data fetching
        self.client.quote_context.subscribe.return_value = (0, "Success")
        
        # Mock DataFrame for the return data
        mock_data = pd.DataFrame({'time_key': ['2023-01-01'], 'close': [150.0]})
        self.client.quote_context.get_cur_kline.return_value = (0, mock_data)
        
        # Call fetch_real_time_data
        result = self.client.fetch_real_time_data("US.AAPL", ["K_DAY"])
        
        # Verify results
        self.assertEqual(result.iloc[0]['close'], 150.0)
        self.client.quote_context.subscribe.assert_called_once_with("US.AAPL", ["K_DAY"])
        self.client.quote_context.get_cur_kline.assert_called_once_with("US.AAPL", 100, "K_DAY")

    def test_fetch_real_time_data_subscription_failure(self):
        """Test handling subscription failure."""
        # Set up mock quote context
        self.client.quote_context = MagicMock()
        
        # Configure mocks for subscription failure
        self.client.quote_context.subscribe.return_value = (1, "Subscription failed")
        
        # Call fetch_real_time_data
        result = self.client.fetch_real_time_data("US.AAPL")
        
        # Verify results
        self.assertTrue(result.empty)
        self.mock_logger.error.assert_called_once_with("Failed to subscribe to US.AAPL: Subscription failed")

    def test_fetch_real_time_data_unsupported_type(self):
        """Test handling unsupported data type."""
        # Set up mock quote context
        self.client.quote_context = MagicMock()
        
        # Configure mocks for successful subscription
        self.client.quote_context.subscribe.return_value = (0, "Success")
        
        # Call fetch_real_time_data with unsupported type
        result = self.client.fetch_real_time_data("US.AAPL", ["UNSUPPORTED_TYPE"])
        
        # Verify results
        self.assertTrue(result.empty)
        self.mock_logger.error.assert_called_once_with("Unsupported subtype: ['UNSUPPORTED_TYPE']")

    def test_place_order_no_context(self):
        """Test placing an order without an initialized trade context."""
        # Ensure no trade context
        self.client.trade_context = None
        
        # Call place_order
        result = self.client.place_order(
            ticker="US.AAPL",
            quantity=10,
            price=150.0,
            order_side=OrderSide.BUY
        )
        
        # Verify results
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Trade context not initialized")
        self.mock_logger.error.assert_called_once()

    def test_place_order_success(self):
        """Test successful order placement."""
        # Set up mock trade context
        self.client.trade_context = MagicMock()
        
        # Configure mock for order placement success
        mock_order_data = pd.DataFrame({
            'order_id': ['12345'],
            'code': ['US.AAPL'],
            'price': [150.0],
            'qty': [10],
            'status': ['SUBMITTED']
        })
        self.client.trade_context.place_order.return_value = (0, mock_order_data)
        
        # Call place_order
        result = self.client.place_order(
            ticker="US.AAPL",
            quantity=10,
            price=150.0,
            order_side=OrderSide.BUY
        )
        
        # Verify results
        self.assertTrue(result["success"])
        self.assertEqual(result["order_id"], "12345")
        self.assertEqual(result["details"]["code"], "US.AAPL")
        self.client.trade_context.place_order.assert_called_once_with(
            price=150.0,
            qty=10,
            code="US.AAPL",
            trd_side=OrderSide.BUY,
            order_type=OrderType.NORMAL,
            trd_env=TrdEnv.SIMULATE,
            time_in_force=TimeInForce.DAY
        )

    def test_place_order_non_us_ticker_warning(self):
        """Test warning for non-US ticker."""
        # Set up mock trade context
        self.client.trade_context = MagicMock()
        
        # Configure mock for order placement success
        mock_order_data = pd.DataFrame({
            'order_id': ['12345'],
            'code': ['AAPL'],
            'price': [150.0],
            'qty': [10],
            'status': ['SUBMITTED']
        })
        self.client.trade_context.place_order.return_value = (0, mock_order_data)
        
        # Call place_order with non-US ticker
        result = self.client.place_order(
            ticker="AAPL",  # Missing US. prefix
            quantity=10,
            price=150.0,
            order_side=OrderSide.BUY
        )
        
        # Verify results
        self.assertTrue(result["success"])
        self.mock_logger.warning.assert_called_once_with(
            "Ticker AAPL may not be a US stock. Consider using 'US.' prefix."
        )

    def test_place_order_failure(self):
        """Test handling order placement failure."""
        # Set up mock trade context
        self.client.trade_context = MagicMock()
        
        # Configure mock for order placement failure
        self.client.trade_context.place_order.return_value = (1, "Order failed")
        
        # Call place_order
        result = self.client.place_order(
            ticker="US.AAPL",
            quantity=10,
            price=150.0,
            order_side=OrderSide.BUY
        )
        
        # Verify results
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Order failed")
        self.mock_logger.error.assert_called_once()

    def test_place_order_exception(self):
        """Test handling exceptions during order placement."""
        # Set up mock trade context
        self.client.trade_context = MagicMock()
        
        # Configure mock to raise an exception
        self.client.trade_context.place_order.side_effect = Exception("API error")
        
        # Call place_order
        result = self.client.place_order(
            ticker="US.AAPL",
            quantity=10,
            price=150.0,
            order_side=OrderSide.BUY
        )
        
        # Verify results
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "API error")
        self.mock_logger.error.assert_called_once()

    @patch('quant.client.futu_client.FutuClient.connect')
    def test_context_manager_enter(self, mock_connect):
        """Test context manager __enter__ method."""
        # Configure mock
        mock_connect.return_value = True
        
        # Use context manager
        with self.client as client:
            # Verify connect was called
            mock_connect.assert_called_once()
            # Verify client is the same instance
            self.assertEqual(client, self.client)

    @patch('quant.client.futu_client.FutuClient.disconnect')
    def test_context_manager_exit(self, mock_disconnect):
        """Test context manager __exit__ method."""
        # Use context manager
        with self.client:
            pass
        
        # Verify disconnect was called
        mock_disconnect.assert_called_once()

if __name__ == "__main__":
    unittest.main()
