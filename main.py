import time
import logging
import os
import sys
from datetime import datetime
import pytz
import pandas as pd

from quant.client.paper_trading_clinet import PaperTradingClient
from quant.client.finrl_client import FinRLClient
from quant.client.realtime_data_client import PolygonClient
from quant.utils.utils import get_spy500_tickers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"quant_trading_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Market hours for US stocks (Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

def is_market_open():
    """Check if the US stock market is currently open."""
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # Check if it's a weekday (0 = Monday, 4 = Friday)
    if now.weekday() > 4:
        return False
    
    # Check if within trading hours
    market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0)
    market_close = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0)
    
    return market_open <= now <= market_close

def get_market_data(symbols, polygon_client):
    """
    Get current market data for the specified symbols using Polygon API.
    
    Args:
        symbols (list): List of stock symbols
        polygon_client (PolygonClient): Instance of the Polygon client
        
    Returns:
        dict: Dictionary containing market data for each symbol
    """
    market_data = {}
    for symbol in symbols:
        try:
            # Get ticker details from Polygon
            ticker_details = polygon_client.get_ticker_details(symbol)
            
            # Extract relevant information from the response
            if hasattr(ticker_details, 'results'):
                price = ticker_details.results.last_trade.price if hasattr(ticker_details.results, 'last_trade') else None
                volume = ticker_details.results.day.volume if hasattr(ticker_details.results, 'day') else None
                
                market_data[symbol] = {
                    'price': price,
                    'volume': volume,
                    'market_cap': ticker_details.results.market_cap if hasattr(ticker_details.results, 'market_cap') else None,
                    'name': ticker_details.results.name if hasattr(ticker_details.results, 'name') else None
                }
            else:
                logger.warning(f"No data available for {symbol}")
                market_data[symbol] = {
                    'price': None,
                    'volume': None,
                    'market_cap': None,
                    'name': None
                }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {str(e)}")
            market_data[symbol] = {
                'price': None,
                'volume': None,
                'market_cap': None,
                'name': None
            }
    
    return market_data

def main():
    """Main function to run the trading system."""
    logger.info("Starting quantitative trading system")
    
    # Initialize clients
    try:
        paper_trading_client = PaperTradingClient()
        finrl_client = FinRLClient()
        polygon_client = PolygonClient()
        
        # Get account information
        account_info = paper_trading_client.get_account_info()
        logger.info(f"Trading account initialized with ${account_info.get('cash', 0)} cash available")
        
        # Get S&P 500 tickers and limit to a manageable number
        # Taking first 10 symbols for easier testing - increase as needed
        all_symbols = get_spy500_tickers()
        symbols = all_symbols[:10]  # Limiting to 10 symbols to avoid API rate limits
        logger.info(f"Using {len(symbols)} symbols from S&P 500")
        
        # Verify symbols are tradable
        tradable_symbols = []
        for symbol in symbols:
            if paper_trading_client.is_tradeable(symbol):
                tradable_symbols.append(symbol)
            
        symbols = tradable_symbols
        logger.info(f"Trading the following symbols: {symbols}")
        
        # Main trading loop
        while True:
            try:
                # Skip if market is closed
                if not is_market_open():
                    logger.info("Market is closed. Waiting...")
                    time.sleep(60)  # Check every minute if market is closed
                    continue
                
                logger.info("Checking for trading opportunities...")
                
                # Get current market data using Polygon client
                market_data = get_market_data(symbols, polygon_client)
                
                # Get current positions
                portfolio = {}
                for symbol in symbols:
                    try:
                        position, _ = paper_trading_client.get_positions(symbol)
                        if position:
                            portfolio[symbol] = position
                    except Exception as e:
                        logger.error(f"Error getting position for {symbol}: {str(e)}")
                
                # Ask model for decisions for each symbol
                for symbol in symbols:
                    try:
                        # Skip symbols with missing market data
                        if symbol not in market_data or market_data[symbol]['price'] is None:
                            logger.warning(f"Skipping {symbol} due to missing market data")
                            continue
                        
                        current_position_qty = 0
                        if symbol in portfolio:
                            current_position_qty = float(portfolio[symbol].get('qty', 0))
                        
                        # Get model's recommendation
                        action, confidence, target_qty = finrl_client.get_action(
                            symbol=symbol,
                            market_data=market_data[symbol],
                            current_position=current_position_qty
                        )
                        
                        logger.info(f"Symbol: {symbol} | Action: {action} | Confidence: {confidence:.2f} | Target Qty: {target_qty}")
                        
                        # Execute trades based on model recommendation
                        if action == "BUY" and confidence > 0.7:
                            buy_qty = target_qty - current_position_qty
                            if buy_qty > 0:
                                logger.info(f"Buying {buy_qty} shares of {symbol}")
                                result = paper_trading_client.buy_market_order(symbol, buy_qty)
                                if result:
                                    logger.info(f"Buy order executed for {symbol}: {buy_qty} shares")
                        
                        elif action == "SELL" and confidence > 0.7:
                            sell_qty = current_position_qty - target_qty
                            if sell_qty > 0:
                                logger.info(f"Selling {sell_qty} shares of {symbol}")
                                result = paper_trading_client.sell_market_order(symbol, sell_qty)
                                if result:
                                    logger.info(f"Sell order executed for {symbol}: {sell_qty} shares")
                    except Exception as e:
                        logger.error(f"Error processing symbol {symbol}: {str(e)}")
                
                # Sleep for 5 seconds before next iteration
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(5)  # Continue after error
    
    except Exception as e:
        logger.error(f"Fatal error in main function: {e}")

if __name__ == "__main__":
    main()
