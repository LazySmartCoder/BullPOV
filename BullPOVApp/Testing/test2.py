from SmartApi import SmartConnect
import pyotp
from credentials import *
from datetime import datetime
from stock_list import stocks

def fetch_stock_details(symbol):
    api_key = smartapi_api_key
    client_code = smartapi_client_id
    mpin = smartapi_pin
    totp_secret = smartapi_totp

    # Generate TOTP
    totp = pyotp.TOTP(totp_secret).now()

    # Connect
    smart_api = SmartConnect(api_key)
    smart_api.generateSession(client_code, mpin, totp)
    smart_api.getfeedToken()

    exchange = "NSE"
    symbol_eq = f"{symbol}-EQ"
    search = smart_api.searchScrip(exchange, symbol)

    data = next((item for item in search["data"] if item["tradingsymbol"] == symbol_eq), None)
    if not data:
        return None

    token = data["symboltoken"]
    tradingsymbol = data["tradingsymbol"]

    # Get live data
    ltp_data = smart_api.ltpData(exchange, tradingsymbol, token)["data"]

    return {
        "Name": data.get("companyname", symbol),
        "Symbol": tradingsymbol,
        "CurrentPrice": float(ltp_data.get("ltp", 0)),
        "DayHigh": float(ltp_data.get("high", 0)),
        "DayLow": float(ltp_data.get("low", 0)),
        "OpeningPrice": float(ltp_data.get("open", 0)),
        "ClosingPrice": float(ltp_data.get("close", 0)),
        "PriceChange": round(float(ltp_data.get("ltp", 0)) - float(ltp_data.get("close", 0)), 2),
        "Volume": int(ltp_data.get("volume", 0)),
        "MktCap": 0,  # SmartAPI doesn't return this
        "PERatio": 0,  # Not available in LTP data
        "DividendYield": 0,  # Not available
        "EPS": 0,  # Not available
        "LastUpdateTime": datetime.now(),
        "UPUsers": 0,  # Custom metric
        "DownUsers": 0,
        "TotalUsers": 0
    }

def fetch_top_gainers():
    # — SmartAPI credentials —
    api_key     = smartapi_api_key
    client_code = smartapi_client_id
    mpin        = smartapi_pin
    totp_secret = smartapi_totp

    # Generate TOTP and login
    smart_api = SmartConnect(api_key)
    totp = pyotp.TOTP(totp_secret).now()
    smart_api.generateSession(client_code, mpin, totp)
    smart_api.getfeedToken()

    # Predefined NIFTY 50 symbols without suffix
    nifty_symbols = list(stocks.keys())

    gainers = []

    for sym in nifty_symbols:
        try:
            # Convert to SmartAPI trading symbol and get token
            search = smart_api.searchScrip("NSE", sym)
            item = next(i for i in search["data"] if i["tradingsymbol"] == f"{sym}-EQ")
            token = item["symboltoken"]
            
            # Get live data
            ltp_data = smart_api.ltpData("NSE", f"{sym}-EQ", token)["data"]
            
            ltp = float(ltp_data["ltp"])
            prev_close = float(ltp_data["close"])
            pct_change = round((ltp - prev_close) / prev_close * 100, 2)

            gainers.append({
                "symbol": f"{sym}.NS",
                "ltp": ltp,
                "change_percent": pct_change
            })
        except Exception:
            continue

    # Sort and display top 5 gainers
    top5 = sorted(gainers, key=lambda x: x["change_percent"], reverse=True)[:5]
    for stock in top5:
        print(f"{stock['symbol']}: ₹{stock['ltp']} (+{stock['change_percent']}%)")

def nifty50_stocks():
    from niftystocks import ns

    nifty_50_symbols = ns.get_nifty50_with_ns()
    print(nifty_50_symbols)
