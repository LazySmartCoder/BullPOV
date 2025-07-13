'''for i, j in stocks.items():
    stock = Stock.objects.get(Symbol = i)
    ticker = yf.Ticker(i)
    info = ticker.info
    stock.Sector = info.get("sector", stock.Sector)
    stock.CurrentPrice = info.get("currentPrice", stock.CurrentPrice)
    stock.DayHigh = info.get("dayHigh", stock.DayHigh)
    stock.DayLow = info.get("dayLow", stock.DayLow)
    stock.OpeningPrice = info.get("open", stock.OpeningPrice)
    stock.ClosingPrice = info.get("previousClose", stock.ClosingPrice)
    stock.PriceChange = round(((info.get("currentPrice", 0) - info.get("open", 0)) / info.get("open", 1)) * 100, 2)
    stock.Volume = info.get("volume", stock.Volume)
    stock.MktCap = info.get("marketCap", stock.MktCap)
    stock.PERatio = info.get("trailingPE", stock.PERatio)
    stock.DividendYield = info.get("dividendYield", stock.DividendYield)
    stock.EPS = info.get("trailingEps", stock.EPS)
    stock.LastUpdateTime = datetime.now()
    stock.save()'''

'''
    # top gainers
    # gainers = fetch_top_gainers(nifty50_stocks())
    # for i in gainers:
    #     try:
    #         top_stock_gainer = Stock.objects.get(Symbol = i)
    #         top_stock_gainer.TopGainer = True
    #         top_stock_gainer.save()
    #     except:
    #         print(i)
    #         continue
'''