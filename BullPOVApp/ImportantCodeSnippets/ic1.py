'''

for i, j in indices.items():
    info = yfinance.Ticker(j).info
    stocks = Stock(Name = i, Symbol = j)
    # stocks.Logo = f"{i[0]}"
    stocks.save()
    
    
    
results = {}
for name, symbol in indices.items():
    ticker = yfinance.Ticker(symbol)
    data = ticker.history(period="1d")
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        open_price = data['Open'].iloc[-1]
        change_percent = ((current_price - open_price) / open_price) * 100
        trend = "up" if change_percent > 0 else "down" if change_percent < 0 else "no"
        results[name] = [round(current_price, 2), round(change_percent, 2), trend]    

info = yfinance.Ticker(j).info
stock = Stock(
    Name = i,
    Symbol = j,
    CurrentPrice=info.get("currentPrice", 0),
    DayHigh=info.get("dayHigh", 0),
    DayLow=info.get("dayLow", 0),
    OpeningPrice=info.get("open", 0),
    ClosingPrice=info.get("previousClose", 0),
    PriceChange=round(info.get("currentPrice", 0) - info.get("previousClose", 0), 2),
    Volume=info.get("volume", 0),
    MktCap=info.get("marketCap", 0),
    PERatio=info.get("trailingPE", 0),
    DividendYield=info.get("dividendYield", 0),
    EPS=info.get("trailingEps", 0),
    LastUpdateTime=datetime.now(),
    UPUsers=0,
    DownUsers=0,
    TotalUsers=0
)
        
'''