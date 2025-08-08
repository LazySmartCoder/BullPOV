from django.shortcuts import render, HttpResponse, redirect
from .updates import *
from django.contrib.auth.models import User
from BullPOVApp.models import *
import subprocess
from django.db.models import F, ExpressionWrapper, IntegerField

# Create your views here.
def adminIndex(request):
    return render(request, "admin-index.html")

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

def indiceUpdate(request):
    index_symbols = ['NSEI', 'BSESN', 'NSEBANK', 'CNXIT', 'NSEMDCP50']

    for symbol in index_symbols:
        ticker = yf.Ticker(f"^{symbol}")

        try:
            fast_data = ticker.fast_info
            current_price = fast_data.get('lastPrice')
            open_price = fast_data.get('open')
            day_high = fast_data.get('dayHigh')
            day_low = fast_data.get('dayLow')
            previous_close = fast_data.get('previousClose')

            if not current_price:
                print(f"Skipping {symbol} due to missing data.")
                continue

            stock, created = Stock.objects.get_or_create(Symbol=symbol)

            stock.CurrentPrice = current_price or 0
            stock.OpeningPrice = open_price or 0
            stock.DayHigh = day_high or 0
            stock.DayLow = day_low or 0
            stock.PreviousCloseYesterday = stock.PreviousCloseToday
            stock.PreviousCloseToday = previous_close or 0
            stock.PriceChange = (current_price - previous_close) if open_price else 0

            stock.save()
            print(f"{'Created' if created else 'Updated'} {symbol}")

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return HttpResponse("Indices Updated!")

def updateStocks(request):
    subprocess.Popen(['python', 'BullPOVAdmin\\updateStocks.py'], shell=True)
    return HttpResponse("All the stocks have been updated.")

def declareResults(request):
    subprocess.Popen(['python', 'BullPOVAdmin\\declareResults.py'], shell=True)
    return HttpResponse("Results have been declared.")

def dataMaintainence(request):
    return HttpResponse("Data maintained.")

def userWithdrawalRequests(request):
    txn = WalletTxn.objects.filter(Action = False, Status = "PENDING")
    return render(request, "uwr.html", {"withdrawals" : txn})

def withdrawn(request, id):
    txn = WalletTxn.objects.get(ID = id)
    user = UserDetail.objects.get(User = txn.User)
    user.WalletBalance = user.WalletBalance - txn.Amount
    user.save()
    txn.TxnID = "N/A"
    txn.DateTime = datetime.now()
    txn.Status = "SUCCESS"
    txn.save()
    return redirect("userWithdrawalRequests")

def updateTrends(request):
    gainer = str(request.GET["gainer"]).split("-")
    loser = str(request.GET["loser"]).split("-")
    volume = str(request.GET["volume"]).split("-")
    Stock.objects.all().update(UPUsers=0, DownUsers=0)
    Stock.objects.all().update(TopGainer = False, TopLoser = False, TopVolume = False)
    for g in gainer:
        s = Stock.objects.get(Symbol = g)
        s.TopGainer = True
        s.save()

    for l in loser:
        s = Stock.objects.get(Symbol = l)
        s.TopLoser = True
        s.save()

    for v in volume:
        s = Stock.objects.get(Symbol = v)
        s.TopVolume = True
        s.save()

    return HttpResponse("Trends Updated.")

