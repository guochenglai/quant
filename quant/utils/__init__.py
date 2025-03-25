import pandas as pd
import requests

def get_spy500_tickers():
    """Fetch the list of S&P 500 tickers from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, verify=False)
    tables = pd.read_html(response.text)
    sp500_table = tables[0]
    return sp500_table['Symbol'].tolist()