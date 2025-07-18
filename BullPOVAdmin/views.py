from django.shortcuts import render, HttpResponse
from BullPOVApp.models import *
import yfinance as yf
from datetime import datetime
from django.db.models import F

# Create your views here.
def index(request):
    return HttpResponse("Welcome to admin panel!")

def update_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BO")
        info = ticker.info

        stock = Stock.objects.get(Symbol=symbol)  # Adjust if key is different

        stock.CurrentPrice = info.get('currentPrice', 0)
        stock.DayHigh = info.get('dayHigh', 0)
        stock.DayLow = info.get('dayLow', 0)
        stock.OpeningPrice = info.get('open', 0)
        stock.PreviousCloseToday = info.get('previousClose', 0)
        stock.PriceChange = round((stock.CurrentPrice - stock.PreviousCloseToday), 2)
        stock.Volume = info.get('volume', 0)
        stock.MktCap = info.get('marketCap', 0)
        stock.PERatio = info.get('trailingPE', 0)
        stock.DividendYield = info.get('dividendYield', 0) or 0
        stock.EPS = info.get('trailingEps', 0)
        stock.LastUpdateTime = datetime.now()

        stock.save()
        return f"{symbol} updated successfully."

    except Stock.DoesNotExist:
        return f"Stock with symbol {symbol} not found in database."
    except Exception as e:
        return f"Error updating {symbol}: {str(e)}"


def update_all_stocks(request):
    stocks = Stock.objects.all()
    for stock in stocks:
        update_stock_data(stock.Symbol)
    return HttpResponse("All stock data updated.")

def keep_top_500_by_market_cap(request):
    # stock = Stock.objects.all()
    # for i in stock:
    #     i.PreviousCloseYesterday = i.PreviousCloseToday
    #     i.save()

    return HttpResponse(f"✅ Kept top 500 by Market Cap. Deleted others.")

def declareResults(request):
    stocks = Stock.objects.annotate(
        total_votes=F('UPUsers') + F('DownUsers')
    ).filter(total_votes__gt=0)
    for i in stocks:
        if i.PreviousCloseToday >= i.PreviousCloseYesterday:
            trade = Trade.objects.filter(Stock = i, Prediction = False, ActiveStatus = True)
            for j in trade:
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.WalletBalance = user.WalletBalance + j.Amount
                user.save()
                j.Return = 0.0
                j.Outcome = False
                j.ActiveStatus = False
                j.save()
            trade = Trade.objects.filter(Stock = i, Prediction = True, ActiveStatus = True)
            for k in trade:
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.WalletBalance = user.WalletBalance + j.Amount + k.Return
                user.save()
                j.Outcome = True
                j.ActiveStatus = False
                j.save()

        else:
            trade = Trade.objects.filter(Stock = i, Prediction = True, ActiveStatus = True)
            for j in trade:
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.WalletBalance = user.WalletBalance + j.Amount
                user.save()
                j.Return = 0.0
                j.Outcome = False
                j.ActiveStatus = False
                j.save()
            trade = Trade.objects.filter(Stock = i, Prediction = False, ActiveStatus = True)
            for k in trade:
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.WalletBalance = user.WalletBalance + j.Amount + k.Return
                user.save()
                j.Outcome = True
                j.ActiveStatus = False
                j.save()


