import time
import os
import sys
from datetime import datetime
import pytz
import pandas as pd

from quant.client.paper_trading_client import PaperTradingClient
from quant.client.finrl_client import FinRLClient
from quant.client.realtime_data_client import PolygonClient
from quant.client.decision_engine import DecisionEngine
from quant.utils.utils import get_spy500_symbols
from quant.logger import configure_logger

# Configure root logger for the application
logger = configure_logger(name='main', log_file='trade')

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

def main():
    """Main function to run the trading system."""
    logger.info("Starting quantitative trading system")
    
    try:
        paper_trading_client = PaperTradingClient(logger=logger)
        polygon_client = PolygonClient(logger=logger)
        decision_engine = DecisionEngine(logger=logger)
        
        # spy500_symbols = get_spy500_symbols(logger)
        spy500_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Example symbols for testing
        logger.info(f"All S&P 500 symbols fetched: {len(spy500_symbols)} symbols : [{spy500_symbols}]")
        
        # Main trading loop
        while True:
            try:
                # Skip if market is closed
                if not is_market_open():
                    logger.info("Market is closed. Waiting 3 minutes...")
                    time.sleep(180)  
                    continue
                
                
                account_info = paper_trading_client.get_account_info()
                logger.info(f"Trading account initialized with ${account_info.get('cash', 0)} cash available")
                
                # Get market data for S&P 500 symbols
                market_data = _get_market_data(spy500_symbols, polygon_client, logger)
                
                # Get current positions 
                portfolio = _get_positions(spy500_symbols, paper_trading_client, logger)
                
                # Ask model for decisions for each symbol
                logger.info(f"======= Trading for sybmbols: {spy500_symbols} =======")
                for symbol in spy500_symbols:
                    try:
                        # Skip symbols with missing market data
                        if symbol not in market_data or market_data[symbol]['price'] is None:
                            logger.warning(f"Skipping {symbol} due to missing market data")
                            continue
                        
                        current_position_qty = 0
                        if symbol in portfolio:
                            current_position_qty = float(portfolio[symbol].get('qty', 0))
                        
                        # Get model's recommendation
                        action, confidence, target_qty = decision_engine.get_action(
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
                
                time.sleep(15)
                logger.info(f"Sleeped for 15 seconds to avoid hitting API too fast for trading loop")
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(15)  # Continue after error
    
    except Exception as e:
        logger.error(f"Fatal error in main function: {e}")


def _get_positions(symbols, paper_trading_client, logger):

    portfolio = {}
    for symbol in symbols:
        try:
            position, portfolio = paper_trading_client.get_positions(symbol)
            if position:
                portfolio[symbol] = position
            time.sleep(15) 
            logger.info(f"Sleeped for 15 seconds to avoid hitting API too fast, for getting positions")
        except Exception as e:
            logger.error(f"Error getting position for {symbol}: {str(e)}")
    return portfolio

def _get_market_data(symbols, polygon_client, logger):
    """
    Get current market data for the specified symbols using Polygon API.
    
    Args:
        symbols (list): List of stock symbols
        polygon_client (PolygonClient): Instance of the Polygon client
        logger (logging.Logger): Logger for this function
        
    Returns:
        dict: Dictionary containing market data for each symbol
    """
    market_data = {}
    for symbol in symbols:
        try:
            # Get symbol details from Polygon
            symbol_details = polygon_client.get_symbol_details(symbol)
            
            # Extract relevant information from the response
            if hasattr(symbol_details, 'results'):
                price = symbol_details.results.last_trade.price if hasattr(symbol_details.results, 'last_trade') else None
                volume = symbol_details.results.day.volume if hasattr(symbol_details.results, 'day') else None
                
                market_data[symbol] = {
                    'price': price,
                    'volume': volume,
                    'market_cap': symbol_details.results.market_cap if hasattr(symbol_details.results, 'market_cap') else None,
                    'name': symbol_details.results.name if hasattr(symbol_details.results, 'name') else None
                }
            else:
                logger.warning(f"No data available for {symbol}")
                market_data[symbol] = {
                    'price': None,
                    'volume': None,
                    'market_cap': None,
                    'name': None
                }
            time.sleep(15) # Rate limit to avoid hitting API too fast
            logger.info(f"Sleeped for 10 seconds to avoid hitting API too fast, for getting market data")
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {str(e)}")
            market_data[symbol] = {
                'price': None,
                'volume': None,
                'market_cap': None,
                'name': None
            }
    
    return market_data


if __name__ == "__main__":
    main()
