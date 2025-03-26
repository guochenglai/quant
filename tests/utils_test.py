import unittest
from quant.utils.utils import *

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant import utils

class UtilsTest(unittest.TestCase):
    
    def test_download_data(self):
        start_date = (datetime.now() - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        ticker_list = ['AAPL', 'MSFT']
        
        # Test if the function returns a DataFrame
        df = download_data(start_date, end_date, ticker_list)
        self.assertIsInstance(df, pd.DataFrame)
        
        # Test if the DataFrame has the expected columns
        columns = df.columns.tolist()
        print (f"DataFrame columns: {columns}")

    def test_get_spy500_tickers(self):
        # Test if the function returns a list
        tickers = get_spy500_tickers()
        
        print (f"SP500 tickers: {tickers}")

        # Test if the list is not empty
        self.assertGreater(len(tickers), 0)
        


if __name__ == "__main__":
    unittest.main()