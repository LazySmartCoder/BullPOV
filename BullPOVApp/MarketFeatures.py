from SmartApi import SmartConnect
import pyotp
from .credentials import *
from datetime import datetime, timedelta
from .stock_list import stocks
import pytz

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

def fetch_top_gainers(l):
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
    nifty_symbols = l

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
        gainers.append(stock['symbol'])
    return gainers

def nifty50_stocks():
    from niftystocks import ns

    symbols_with_ns = ns.get_nifty50_with_ns()
    cleaned_symbols = [symbol.strip().replace('.NS', '') for symbol in symbols_with_ns]
    return cleaned_symbols

def fetch_top_losers(l):
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
    nifty_symbols = l

    losers = []

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

            losers.append({
                "symbol": f"{sym}.NS",
                "ltp": ltp,
                "change_percent": pct_change
            })
        except Exception:
            continue

    # Sort by least percent change (most negative), i.e., biggest losers
    top5 = sorted(losers, key=lambda x: x["change_percent"])[:5]
    result = [stock["symbol"] for stock in top5]
    return result

def get_today_high_low(symbol):
    try:
        # 1. Authenticate
        api = SmartConnect(api_key=smartapi_api_key)
        totp_token = pyotp.TOTP(smartapi_totp).now()
        session = api.generateSession(
            clientCode=smartapi_client_id,
            password=smartapi_pin,
            totp=totp_token
        )
        if not session.get("status"):
            raise RuntimeError("Login failed: " + str(session))

        # 2. Search Scrip & Get Token
        search = api.searchScrip(exchange="NSE", searchscrip=symbol.upper())
        if not search.get("status") or not search.get("data"):
            raise ValueError(f"Symbol '{symbol}' not found.")
        token = search["data"][0]["symboltoken"]

        # 3. Try OHLC mode
        response = api.getMarketData(
            mode="OHLC",
            exchangeTokens={"NSE": [token]}
        )

        fetched = response.get("data", {}).get("fetched", [])
        if fetched:
            low = float(fetched[0]["low"])
            high = float(fetched[0]["high"])
            return [low, high]

        # 4. Fallback to FULL mode
        response = api.getMarketData(
            mode="FULL",
            exchangeTokens={"NSE": [token]}
        )

        fetched = response.get("data", {}).get("fetched", [])
        if fetched:
            low = float(fetched[0]["low"])
            high = float(fetched[0]["high"])
            return [low, high]

        raise RuntimeError("No market data returned")

    except Exception as e:
        print(f"Error fetching today's high/low for {symbol}: {e}")
        return [None, None]