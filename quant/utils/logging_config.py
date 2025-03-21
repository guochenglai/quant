import logging
import os
from datetime import datetime

def setup_logger(name='quant'):
    """
    Configure and return a logger with file and console handlers.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Configured logger object
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger(name)
    
    # Only configure handler if it hasn't been configured before
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create file handler with timestamp in filename
        log_file = f"{name.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
