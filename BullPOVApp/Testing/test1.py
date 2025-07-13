# import yfinance as yf

# # Define the ticker symbols
# indices = {
#     "NIFTY 50": "^NSEI",
#     "SENSEX": "^BSESN",
#     "BANKNIFTY": "^NSEBANK"
# }

# # Fetch the data
# results = {}
# for name, symbol in indices.items():
#     ticker = yf.Ticker(symbol)
#     data = ticker.history(period="1d")
    
#     if not data.empty:
#         current_price = data['Close'].iloc[-1]
#         open_price = data['Open'].iloc[-1]
#         change_percent = ((current_price - open_price) / open_price) * 100
#         trend = "up" if change_percent > 0 else "down" if change_percent < 0 else "no"
#         results[name] = [round(current_price, 2), round(change_percent, 2), trend]
# print(results)


# important code for share insertion into database
import requests
import yfinance as yf

companies = {
    "company_1": "Reliance Industries Ltd",
    "company_2": "HDFC Bank Ltd.",
    "company_3": "Tata Consultancy Services Ltd.",
    "company_4": "Bharti Airtel Ltd.",
    "company_5": "ICICI Bank Ltd.",
    "company_6": "State Bank Of India",
    "company_7": "Infosys Ltd.",
    "company_8": "Life Insurance Corporation Of India",
    "company_9": "Bajaj Finance Ltd.",
    "company_10": "Hindustan Unilever Ltd.",
    "company_11": "ITC Ltd.",
    "company_12": "Larsen & Toubro Ltd.",
    "company_13": "HCL Technologies Ltd.",
    "company_14": "Kotak Mahindra Bank Ltd.",
    "company_15": "Sun Pharmaceutical Industries Ltd.",
    "company_16": "Maruti Suzuki India Ltd.",
    "company_17": "Mahindra & Mahindra Ltd.",
    "company_18": "UltraTech Cement Ltd."
}

def get_symbol_from_name(company_name):
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": company_name, "region": "IN", "lang": "en-US"}

    try:
        r = requests.get(url, params=params)
        data = r.json()
        for item in data.get("quotes", []):
            if item.get("exchange") in ["NSI", "BSE"]:
                return item.get("symbol")
    except:
        pass
    return None

# Fetch and print symbols + current market price using yfinance
symbol_data = {}
for key, name in companies.items():
    symbol = get_symbol_from_name(name)
    if symbol:
        ticker = yf.Ticker(symbol)
        price = ticker.info.get("currentPrice")
        symbol_data[name] = {
            "symbol": symbol,
            "price": price
        }
        print(f"{name} - {symbol} - ₹{price}")
    else:
        print(f"{name} - Symbol not found")

