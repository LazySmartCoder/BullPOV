from django.shortcuts import render, HttpResponse
from BullPOVApp.models import *
import yfinance as yf
from datetime import datetime
from django.db.models import F
from django.db.models import Sum

# Create your views here.
def index(request):
    return render(request, "admin-index.html")

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


def updateStocks(request):
    stocks = Stock.objects.all()
    count = 0
    for stock in stocks:
        update_stock_data(stock.Symbol)
        count += 1
        print(count)
    return HttpResponse("All stock data updated.")

def dataClean(request):
    return HttpResponse(f"Done Something.")

def declareResults(request):
    stocks = Stock.objects.annotate(
        total_votes=F('UPUsers') + F('DownUsers')
    ).filter(total_votes__gt=0)
    for i in stocks:
        # losing party variable
        totaluplose = 0
        totaldownlose = 0

        if i.PreviousCloseToday > i.PreviousCloseYesterday:
            trade = Trade.objects.filter(Stock = i, Prediction = False, ActiveStatus = True)
            for j in trade:
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.save()
                j.Return = 0.0
                j.Outcome = False
                j.ActiveStatus = False
                j.save()
                totaldownlose += j.Amount
            trade = Trade.objects.filter(Stock = i, Prediction = True, ActiveStatus = True)
            total_amount = Trade.objects.filter(Stock=i, Prediction=True, ActiveStatus=True).aggregate(total=Sum('Amount'))['total'] or 0
            for j in trade:
                userPercent = j.Amount / total_amount * 100
                userReturn = userPercent / 100 * totaldownlose
                j.Return = userReturn
                j.Outcome = True
                j.ActiveStatus = False
                j.save()
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.WalletBalance = user.WalletBalance + j.Amount + j.Return
                user.save()

        else:
            trade = Trade.objects.filter(Stock = i, Prediction = True, ActiveStatus = True)
            for j in trade:
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.save()
                j.Return = 0.0
                j.Outcome = False
                j.ActiveStatus = False
                j.save()
                totaluplose += j.Amount
            trade = Trade.objects.filter(Stock = i, Prediction = False, ActiveStatus = True)
            total_amount = Trade.objects.filter(Stock=i, Prediction=False, ActiveStatus=True).aggregate(total=Sum('Amount'))['total']
            for j in trade:
                userPercent = j.Amount / total_amount * 100
                userReturn = userPercent / 100 * totaluplose
                j.Return = userReturn
                j.Outcome = True
                j.ActiveStatus = False
                j.save()
                user = UserDetail.objects.get(User = j.Trader)
                user.InvestedBalance = user.InvestedBalance - j.Amount
                user.WalletBalance = user.WalletBalance + j.Amount + j.Return
                user.save()
    return HttpResponse("Results Declared!")

def indiceUpdate(request):
    index_symbols = ['^NSEI', '^BSESN', '^NSEBANK', '^CNXIT', '^NSEMDCP50']

    for symbol in index_symbols:
        ticker = yf.Ticker(symbol)

        try:
            fast_data = ticker.fast_info
            current_price = fast_data.get('lastPrice')
            open_price = fast_data.get('open')
            day_high = fast_data.get('dayHigh')
            day_low = fast_data.get('dayLow')
            previous_close = fast_data.get('previousClose')
            volume = fast_data.get('volume')

            if not current_price:
                print(f"Skipping {symbol} due to missing data.")
                continue

            stock, created = Stock.objects.get_or_create(Symbol=symbol)

            stock.CurrentPrice = current_price or 0
            stock.OpeningPrice = open_price or 0
            stock.DayHigh = day_high or 0
            stock.DayLow = day_low or 0
            stock.PreviousCloseToday = previous_close or 0
            stock.Volume = volume or 0
            stock.PriceChange = (current_price - open_price) if open_price else 0
            stock.LastUpdateTime = datetime.now()

            stock.save()
            print(f"{'Created' if created else 'Updated'} {symbol}")

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return HttpResponse("Indices Updated!")

def closeTrading(request):
    user = User.objects.get(username = "anni")
    user.last_name = "close"
    user.save()
    return HttpResponse("Trading Closed.")

def openTrading(request):
    user = User.objects.get(username = "anni")
    user.last_name = "open"
    user.save()
    return HttpResponse("Trading Started.")