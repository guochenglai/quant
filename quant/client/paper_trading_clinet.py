from alpaca.trading.client import TradingClient
import os

class PaperTradingClient:
    def __init__(self):
        alpaca_api_key = os.getenv('APCA_API_KEY_ID')
        alpaca_secret_key = os.getenv('APCA_API_SECRET_KEY')
        self.paper_trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
        
        

   