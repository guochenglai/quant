from alpaca.trading.client import TradingClient

class PaperTradingClient:
    def __init__(self):
        self.paper_trading_client = TradingClient('api-key', 'secret-key', paper=True)
        
        

   