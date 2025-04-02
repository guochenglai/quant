from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
from alpaca.trading.requests import TrailingStopOrderRequest
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

import os, json
from uuid import UUID

class PaperTradingClient:
    def __init__(self):
        alpaca_api_key = os.getenv('APCA_API_KEY_ID')
        alpaca_secret_key = os.getenv('APCA_API_SECRET_KEY')
        self.paper_trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    

    def get_account_info(self):
        """
        Fetch account information from Alpaca API.
        """
        account = self.paper_trading_client.get_account()
        
        # Convert account object to a serializable dictionary
        try:
            # Try Pydantic model methods first
            if hasattr(account, "model_dump"):  # Pydantic v2
                account_dict = account.model_dump()
            elif hasattr(account, "dict"):  # Pydantic v1
                account_dict = account.dict()
            else:
                # Create dictionary manually from object attributes
                account_dict = {}
                for attr in dir(account):
                    if not attr.startswith('_') and not callable(getattr(account, attr)):
                        account_dict[attr] = getattr(account, attr)
                
            # Print as JSON, converting any remaining non-serializable objects to strings
            print(f"=================== Got Account Info ==================== \n: {json.dumps(account_dict, indent=4, default=str)}")
        except Exception as e:
            # Fallback to printing object attributes
            print(f"Account Info (not serializable to JSON): {account}")
            print(f"Error during serialization: {e}")
        
        return account_dict


    def get_positions(self, symbol):
        """
        Fetch positions from Alpaca API.
        """
        try:
            position = self.paper_trading_client.get_open_position(symbol)
            print(f"=================== Got Position Info ==================== \n: {json.dumps(position, indent=4, default=str)}")
            
            portfolio = self.paper_trading_client.get_all_positions()

            print(f"=================== Got All Positions ==================== \n: {json.dumps(portfolio, indent=4, default=str)}")

            return position, portfolio
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return None

    def get_all_orders(self):
        """
        Fetch all orders from Alpaca API.
        """
        try:
            get_orders_request = GetOrdersRequest(
                status=QueryOrderStatus.CLOSED,
                limit=100,
                nested=True  # show nested multi-leg orders
            )
            orders = self.paper_trading_client.get_orders(filter=get_orders_request)
            
            orders_list = [order.model_dump() for order in orders]
            print(f"=================== Got All Orders ==================== \n: {json.dumps(orders_list, indent=4, default=str)}")
            return orders_list
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return None

    def is_tradeable(self, symbol):
        """
        Check if a symbol is tradable.
        """
        try:
            asset = self.paper_trading_client.get_asset(symbol)
            print(f"=================== Got Asset Info ==================== \n: {json.dumps(asset, indent=4, default=str)}")
            return asset.tradable
        except Exception as e:
            print(f"Error fetching asset info for {symbol}: {e}")
            return False

    def buy_market_order(self, symbol, qty):
        """
        Place a market order.
        """
        try:
            order_id = str(UUID(int=0))
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                client_order_id = order_id,  
            )
            
            market_order = self.paper_trading_client.submit_order(
                order_data=market_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(market_order, indent=4, default=str)}")
            return market_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def sell_market_order(self, symbol, qty):
        """
        Place a market order.
        """
        try:
            order_id = str(UUID(int=0))
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                client_order_id = order_id
            )
            
            market_order = self.paper_trading_client.submit_order(
                order_data=market_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(market_order, indent=4, default=str)}")
            return market_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def buy_limit_order(self, symbol, qty, limit_price):
        """
        Place a limit order.
        """
        try:
            order_id = str(UUID(int=0))
            limit_order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY,
                client_order_id = order_id
            )
            
            limit_order = self.paper_trading_client.submit_order(
                order_data=limit_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(limit_order_data, indent=4, default=str)}")
            return limit_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def sell_limit_order(self, symbol, qty, limit_price):
        """
        Place a limit order.
        """
        try:
            order_id = str(UUID(int=0))
            limit_order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY,
                client_order_id = order_id
            )
            
            limit_order = self.paper_trading_client.submit_order(
                order_data=limit_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(limit_order_data, indent=4, default=str)}")
            return limit_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def buy_shorts(self, symbol, qty):
        """
        Place a short order.
        """
        try:
            order_id = str(UUID(int=0))
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
                client_order_id = order_id
            )
            
            market_order = self.paper_trading_client.submit_order(
                order_data=market_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(market_order, indent=4, default=str)}")
            return market_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def sell_shorts(self, symbol, qty):
        """
        Place a short order.
        """
        try:
            order_id = str(UUID(int=0))
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
                client_order_id = order_id
            )
            
            market_order = self.paper_trading_client.submit_order(
                order_data=market_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(market_order, indent=4, default=str)}")
            return market_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def buy_bracket_order(self, symbol, qty, limit_price, stop_loss_price):
        """
        Place a bracket order.
        """
        try:
            order_id = str(UUID(int=0))
            bracket_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                order_class=OrderClass.BRACKET,
                take_profit=TakeProfitRequest(limit_price=limit_price),
                stop_loss=StopLossRequest(stop_price=stop_loss_price),
                client_order_id = order_id
            )
            
            bracket_order = self.paper_trading_client.submit_order(
                order_data=bracket_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(bracket_order, indent=4, default=str)}")
            return bracket_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def sell_bracket_order(self, symbol, qty, limit_price, stop_loss_price):
        """
        Place a bracket order.
        """
        try:
            order_id = str(UUID(int=0))
            bracket_order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                order_class=OrderClass.BRACKET,
                take_profit=TakeProfitRequest(limit_price=limit_price),
                stop_loss=StopLossRequest(stop_price=stop_loss_price),
                client_order_id = order_id
            )
            
            bracket_order = self.paper_trading_client.submit_order(
                order_data=bracket_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(bracket_order, indent=4, default=str)}")
            return bracket_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def buy_trailing_percent_order(self, symbol, qty, trail_percent):
        """
        Place a trailing percent order.
        """
        try:
            order_id = str(UUID(int=0))
            trailing_order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
                trail_percent=trail_percent,
                client_order_id = order_id
            )
            
            trailing_order = self.paper_trading_client.submit_order(
                order_data=trailing_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(trailing_order, indent=4, default=str)}")
            return trailing_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def sell_trailing_percent_order(self, symbol, qty, trail_percent):
        """
        Place a trailing percent order.
        """
        try:
            order_id = str(UUID(int=0))
            trailing_order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
                trail_percent=trail_percent,
                client_order_id = order_id
            )
            
            trailing_order = self.paper_trading_client.submit_order(
                order_data=trailing_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(trailing_order, indent=4, default=str)}")
            return trailing_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def buy_trailing_price_order(self, symbol, qty, trail_price):
        """
        Place a trailing price order.
        """
        try:
            order_id = str(UUID(int=0))
            trailing_order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
                trail_price=trail_price,
                client_order_id = order_id
            )
            
            trailing_order = self.paper_trading_client.submit_order(
                order_data=trailing_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(trailing_order, indent=4, default=str)}")
            return trailing_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None
    
    def sell_trailing_price_order(self, symbol, qty, trail_price):
        """
        Place a trailing price order.
        """
        try:
            order_id = str(UUID(int=0))
            trailing_order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
                trail_price=trail_price,
                client_order_id = order_id
            )
            
            trailing_order = self.paper_trading_client.submit_order(
                order_data=trailing_order_data
            )

            print(f"=================== Order Submitted ==================== \n: OrderId: {order_id}  OrderDetails: {json.dumps(trailing_order, indent=4, default=str)}")
            return trailing_order
        except Exception as e:
            print(f"Error placing order for {symbol}: {e}")
            return None