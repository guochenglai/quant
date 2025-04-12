import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from quant.constants import project_root_dir

# Keep track of configured loggers to avoid duplicate handlers
_configured_loggers = {}

def configure_logger(
    name: str = 'quant',
    log_dir: str = None,
    log_file: str = None,
    log_level: int = logging.INFO,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    is_test: bool = False,
    test_file_name: str = None
) -> logging.Logger:
    """
    Configure and return a logger. If the logger already exists, return it.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        log_file: Name of the log file (without timestamp - will be added)
        log_level: Overall logging level
        console_level: Logging level for console output
        file_level: Logging level for the file handler
        is_test: Whether this is being called from a test
        test_file_name: Name of the test file (without extension) when is_test=True
        
    Returns:
        logging.Logger: Configured logger object
    """
    # If logger has been configured before, just return it
    if name in _configured_loggers:
        return _configured_loggers[name]
    
    # Create log directory
    if log_dir is None:
        log_dir = os.path.join(project_root_dir, '../logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Create and configure file handler
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if is_test and test_file_name:
        # For test cases, use test file name
        log_filename = f"{test_file_name}.{timestamp}.log"
    else:
        # For regular execution, use specified log_file or default to 'trade'
        base_name = log_file if log_file else 'trade'
        log_filename = f"{base_name}.{timestamp}.log"
    
    file_path = os.path.join(log_dir, log_filename)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(file_level)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging configured. Log file: {file_path}")
    
    # Remember this logger
    _configured_loggers[name] = logger
    
    return logger

# Add get_logger as an alias for configure_logger for backward compatibility
def get_logger(name: str = 'quant', **kwargs) -> logging.Logger:
    """
    Get or create a logger with the specified name.
    This is an alias for configure_logger to maintain backward compatibility.
    
    Args:
        name: Name for the logger
        **kwargs: Additional arguments to pass to configure_logger
        
    Returns:
        logging.Logger: The logger instance
    """
    return configure_logger(name=name, **kwargs)

def setup_test_logger(test_file_name: str, **kwargs) -> logging.Logger:
    """
    Set up logging specifically for a test file.
    
    Args:
        test_file_name: Name of the test file (without extension)
        **kwargs: Additional arguments to pass to configure_logger
        
    Returns:
        logging.Logger: The configured test logger
    """
    return configure_logger(
        is_test=True,
        test_file_name=test_file_name,
        **kwargs
    )

def shutdown_logging():
    """
    Properly shutdown all logging handlers.
    """
    logging.shutdown()
