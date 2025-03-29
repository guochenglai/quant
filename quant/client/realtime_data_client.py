import os
from polygon import RESTClient
from quant.utils.logging_config import setup_logger

logger = setup_logger('quant.reaqkl_client')

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