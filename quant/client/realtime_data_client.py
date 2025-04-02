import os
from polygon import RESTClient
from alpaca.data.live import StockDataStream
from quant.utils.logging_config import setup_logger

logger = setup_logger('quant.realtime_data_client')

class PolygonClient:
    """
    The free user can get 5 requests per second and 500,000 requests per month, for Polygon API.
    Detailed information can be found at https://polygon.io/docs/getting-started
    """
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.rest_client = RESTClient(self.api_key)

    def get_tick_list(self, market: str = "stocks", active: str = "true", order: str = "asc", limit: int = 100, sort: str = "ticker"):
        """
        Get a list of tickers from Polygon API.
        
        Args:
            market (str): The market to get tickers from. Default is "stocks".
            active (str): Whether to get active tickers. Default is "true".
            order (str): The order of the tickers. Default is "asc".
            limit (int): The maximum number of tickers to return. Default is 100.
            sort (str): The sorting criteria. Default is "ticker".

        Returns:
            dict: A response containing:
                - count (int): Total number of results
                - next_url (str): URL to fetch the next page of data (if available)
                - request_id (str): ID assigned by the server
                - results (list): Array of ticker objects matching the query
                
        """
        
        ticks  = self.rest_client.list_tickers(
            market=market,
            active=active,
            order=order,
            limit=limit,
            sort=sort)
        
        return ticks

    def get_ticker_details(self, ticker: str):
        """
        Get details of a specific ticker from Polygon API.
        
        Args:
            ticker (str): The ticker symbol to get details for.

        Returns:
            dict: A response containing:
                - request_id (str): ID assigned by the server
                - results (dict): Details of the specified ticker
        """
        
        details = self.rest_client.get_ticker_details(ticker)
        
        return details

    def get_ticker_types(self, ticker: str):
        """
        Get types of a specific ticker from Polygon API.
        
        Args:
            ticker (str): The ticker symbol to get types for.

        Returns:
            dict: A response containing:
                - request_id (str): ID assigned by the server
                - results (list): Array of types for the specified ticker
        """
        
        types = self.rest_client.get_ticker_types(ticker)
        
        return types
    
    def get_related_companies(self, ticker: str):
        """
        Get related companies for a specific ticker from Polygon API.
        
        Args:
            ticker (str): The ticker symbol to get related companies for.

        Returns:
            dict: A response containing:
                - request_id (str): ID assigned by the server
                - results (list): Array of related companies for the specified ticker
        """
        
        related = self.rest_client.get_related_companies(ticker)
        
        return related

class AlPacaClient:
    """
    The free user can get 5 requests per second and 500,000 requests per month, for Alpaca API.
    Detailed information can be found at https://alpaca.markets/docs/api-documentation/api-v2/
    """
    def __init__(self):
        self.api_key = os.getenv("APCA_API_KEY_ID")
        self.secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    def get_ticker_details(self, ticker: str):
        """
        Get details of a specific ticker from Alpaca API.
        
        Args:
            ticker (str): The ticker symbol to get details for.

        Returns:
            dict: A response containing details of the specified ticker.
        """
        
        print("Getting ticker details from Alpaca API...")
        stock_stream = StockDataStream(self.api_key, self.secret_key)
        async def quote_data_handler(data):
            # quote data will arrive here
            print("stock_data:" + data)

        stock_stream.subscribe_quotes(quote_data_handler, ticker)

        stock_stream.run()

class RealtimeDataClient:
    def __init__(self):
        self.polygon_client = PolygonClient()
        self.alpaca_client = AlPacaClient()
    
    def get_ticker_details(self, ticker: str):
        """
        Get details of a specific ticker from both Polygon and Alpaca APIs.
        
        Args:
            ticker (str): The ticker symbol to get details for.

        Returns:
            dict: A response containing details of the specified ticker from both APIs.
        """
        
        polygon_details = self.polygon_client.get_ticker_details(ticker)
        alpaca_details = self.alpaca_client.get_ticker_details(ticker)
        
        return {
            "polygon": polygon_details,
            "alpaca": alpaca_details
        }