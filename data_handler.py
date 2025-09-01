# data_handler.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(ticker: str) -> pd.DataFrame:
    """
    Recupera i dati storici per un dato ticker dagli ultimi 2 anni.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)
    
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return None
        return data
    except Exception as e:
        print(f"Errore durante il recupero dei dati per {ticker}: {e}")
        return None
