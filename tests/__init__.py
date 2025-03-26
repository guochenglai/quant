import unittest
import sys
import os
import logging

# Configure logging
def setup_logger():
    logger = logging.getLogger('quant_tests')
    logger.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create file handler
    file_handler = logging.FileHandler(os.path.join(logs_dir, 'tests.log'))
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

# Add the parent directory to sys.path to allow importing the quant package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant.utils import *


class TestUtils(unittest.TestCase):
    """Test cases for utility functions in the quant package."""
    
    def setUp(self):
        """Set up test fixtures, if any."""
        logger.info(f"Setting up test: {self._testMethodName}")
    
    def tearDown(self):
        """Tear down test fixtures, if any."""
        logger.info(f"Tearing down test: {self._testMethodName}")
    
    def test_fetch_real_data_from_futu(self):
        logger.info("Testing fetch_real_time_data function")
        try:
            data = fetch_real_time_data("US.AAPL")
            logger.info(f"Successfully fetched data for US.AAPL")
            self.assertIsNotNone(data)
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise
        
    
if __name__ == "__main__":
    logger.info("Starting test execution")
    unittest.main()
    logger.info("Test execution completed")