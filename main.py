import yfinance as yf
from datetime import datetime, timedelta
def get_previous_date():
    yesterday = datetime.today() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_previous_close(symbol: str, date_str: str):
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = target_date - timedelta(days=10)  # fetch at least 10 days before (to skip weekends/holidays)
    
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=date_str, interval="1d")
    
    if not data.empty:
        # Get the last available close before target_date
        previous_close = data["Close"].iloc[-1]
        return float(previous_close)
    else:
        return None  # No valid trading data found

# Example usage
print(get_previous_close("YESBANK.BO", "2025-08-14"))