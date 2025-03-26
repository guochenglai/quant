from alpaca_trade_api.rest import REST, TimeFrame
import os
from utils.logging_config import setup_logger
logger = setup_logger('quant.trade_with_futu')
logger.info("Starting trade")

API_KEY = os.getenv('FUTU_API_KEY')
SECRET_KEY = os.getenv('FUTU_SECRET_KEY')

api = REST(API_KEY, SECRET_KEY, base_url='https://paper-api.alpaca.markets')
account = api.get_account()

def submit_order(symbol, qty, side, order_type='market', time_in_force='gtc'):
    """
    Submit an order to Alpaca
    """
    try:
        bars = api.get_barset(symbol, 'minute', limit=5)
        logger.info(f"trade {symbol} bars: {bars}")
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force,
        )
        logger.info(f"Order submitted: {order}")
    except Exception as e:
        logger..error(f"Error submitting order: {e}")
