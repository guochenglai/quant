from futu import OpenQuoteContext, OpenUSTradeContext, TrdEnv, OrderType, TrdSide, TimeInForce
import pandas as pd
from typing import Dict, Any, Optional, Union, List
from quant.utils.logging_config import setup_logger

logger = setup_logger('quant.finrl_client')

class FutuClient:
    """
    Client for interacting with Futu's API for data git fetching and trading in US market.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 11111, 
                 trade_host: str = "127.0.0.1", trade_port: int = 11111,
                 trade_password: Optional[str] = None, 
                 trd_env: TrdEnv = TrdEnv.REAL):
        """
        Initialize the Futu client for US market trading.
        
        Args:
            host: IP address of the quote server
            port: Port of the quote server
            trade_host: IP address of the trade server
            trade_port: Port of the trade server
            trade_password: Trading password
            trd_env: Trading environment, either REAL or SIMULATE
            logger: Logger instance
        """
        self.host = host
        self.port = port
        self.trade_host = trade_host
        self.trade_port = trade_port
        self.trade_password = trade_password
        self.trd_env = trd_env
        self.logger = logger  # Assign the module-level logger to the instance
        
        # Quote context for data fetching
        self.quote_context = None
        
        # Trade context for executing trades
        self.trade_context = None
    
    def connect(self) -> bool:
        """
        Connect to Futu's servers for both data and US market trading.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Connect for data fetching
            self.quote_context = OpenQuoteContext(host=self.host, port=self.port)
            
            # Connect for US market trading if trading password is provided
            if self.trade_password:
                # First initialize the trade context without password
                self.trade_context = OpenUSTradeContext(host=self.trade_host, 
                                                      port=self.trade_port,
                                                      trd_env=self.trd_env)
                
                # Then unlock the trade context with the password
                if self.trade_context:
                    ret, data = self.trade_context.unlock_trade(password=self.trade_password)
                    if ret != 0:
                        self.logger.error(f"Failed to unlock trade context: {data}")
                        return False
            
            self.logger.info("Successfully connected to Futu servers for US market")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Futu servers: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from Futu's servers.
        """
        if self.quote_context:
            self.quote_context.close()
        
        if self.trade_context:
            self.trade_context.close()
        
        self.logger.info("Disconnected from Futu servers")
    
    def fetch_real_time_data(self, ticker: str, subtype: List[str] = None) -> pd.DataFrame:
        """
        Fetch real-time data for a specific ticker.
        
        Args:
            ticker: The ticker symbol (e.g., "HK.00700" for Tencent)
            subtype: List of data types to subscribe to. If None, subscribes to quotes.
                     Options include: "QUOTE", "ORDER_BOOK", "K_1M", "K_5M", "K_15M",
                     "K_30M", "K_60M", "K_DAY", "K_WEEK", "K_MONTH"
        
        Returns:
            DataFrame containing the requested data
        """
        if not self.quote_context:
            self.logger.error("Quote context not initialized. Call connect() first.")
            return pd.DataFrame()
        
        subtype = subtype or ["QUOTE"]
        
        try:
            # Subscribe to the data
            ret, err_message = self.quote_context.subscribe(ticker, subtype)
            if ret != 0:
                self.logger.error(f"Failed to subscribe to {ticker}: {err_message}")
                return pd.DataFrame()
            
            # Get the data based on subtype
            if "QUOTE" in subtype:
                ret, data = self.quote_context.get_stock_quote(ticker)
            elif "ORDER_BOOK" in subtype:
                ret, data = self.quote_context.get_order_book(ticker)
            elif any(k in subtype for k in ["K_1M", "K_5M", "K_15M", "K_30M", "K_60M", "K_DAY", "K_WEEK", "K_MONTH"]):
                k_type = next((k for k in subtype if k.startswith("K_")), "K_DAY")
                ret, data = self.quote_context.get_cur_kline(ticker, 100, k_type)
            else:
                self.logger.error(f"Unsupported subtype: {subtype}")
                return pd.DataFrame()
            
            if ret != 0:
                self.logger.error(f"Failed to get data for {ticker}: {data}")
                return pd.DataFrame()
            
            return data
        except Exception as e:
            self.logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()
    
    def place_order(self, ticker: str, quantity: int, price: float, order_side: TrdSide, 
                    order_type: OrderType = OrderType.NORMAL, time_in_force: TimeInForce = TimeInForce.DAY) -> Dict[str, Any]:
        """
        Place a trade order for a specific US market ticker.
        
        Args:
            ticker: The ticker symbol (e.g., "US.AAPL" for Apple)
            quantity: Number of shares to trade
            price: Price at which to execute the trade
            order_side: Whether to buy (BUY) or sell (SELL)
            order_type: Type of order (NORMAL, MARKET, LIMIT, etc.)
            time_in_force: How long the order remains active
            
        Returns:
            Dictionary containing order details and status
        """
        if not self.trade_context:
            self.logger.error("Trade context not initialized. Call connect() with trade_password.")
            return {"success": False, "error": "Trade context not initialized"}
        
        try:
            # Check if ticker has US market prefix
            if not ticker.startswith("US."):
                self.logger.warning(f"Ticker {ticker} may not be a US stock. Consider using 'US.' prefix.")
            
            # Place the order for US market
            ret, data = self.trade_context.place_order(
                price=price,
                qty=quantity,
                code=ticker,
                trd_side=order_side,
                order_type=order_type,
                trd_env=self.trd_env,
                time_in_force=time_in_force
            )
            
            if ret != 0:
                self.logger.error(f"Failed to place US market order for {ticker}: {data}")
                return {"success": False, "error": data}
            
            order_id = data.iloc[0]['order_id']
            self.logger.info(f"US market order placed successfully. Order ID: {order_id}")
            
            return {"success": True, "order_id": order_id, "details": data.to_dict('records')[0]}
            
        except Exception as e:
            self.logger.error(f"Error placing US market order for {ticker}: {e}")
            return {"success": False, "error": str(e)}
    
    def __enter__(self):
        """Context manager entry point"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        self.disconnect()
