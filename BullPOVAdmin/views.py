from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from BullPOVApp.models import *
import subprocess
from django.db.models import F, ExpressionWrapper, IntegerField
from datetime import datetime, timedelta
import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from BullPOVApp.credentials import *
from BullPOVApp.emailTemplates import *

def sendEmail(sender, receiver, subject, message):
    sender_email = sender
    sender_password = google_app_password
    msg = MIMEMultipart("alternative")
    msg["From"] = f"BullPOV <{sender_email}>"
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("contact.bullpov@gmail.com", sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        return None
    except Exception as e:
        print(f"Error sending email: {e}")

# Create your views here.
def adminIndex(request):
    stocks = Stock.objects.annotate(
        total_votes=ExpressionWrapper(F("UPUsers") + F("DownUsers"), output_field=IntegerField())
    ).filter(total_votes__gt=0)
    amt_list_up = []
    amt_list_down = []
    for i in stocks:
        up = 0
        trades = Trade.objects.filter(Stock = i, Prediction = True)
        for t in trades:
            up += t.Amount
        down = 0
        trades = Trade.objects.filter(Stock = i, Prediction = False)
        for t in trades:
            down += t.Amount
        amt_list_up.append(up)
        amt_list_down.append(down)
    return render(request, "admin-index.html", {"data" : zip(stocks, amt_list_up, amt_list_down)})

def platformCut(request):
    cuts = request.POST.getlist("cuts[]")
    for i in cuts:
        symbol = i.split("-")[0]
        cut = i.split("-")[1]
        stock = Stock.objects.get(Symbol = symbol)
        stock.PlatformCut = cut
        stock.save()
    return HttpResponse("Platform Cut assigned.")

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

def get_previous_date():
    yesterday = datetime.today() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_previous_close(symbol: str, date_str: str):
    # Parse the date
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    # Get one trading day before the target date
    prev_day = target_date - timedelta(days=1)
    ticker = yf.Ticker(symbol)
    # Fetch history from prev_day to target_date
    data = ticker.history(start=prev_day.strftime("%Y-%m-%d"), end=date_str, interval="1d")
    if not data.empty:
        # 'Close' column's last value is the previous close
        return data["Close"].iloc[-1]
    else:
        return 0  # No data (holiday, weekend, or invalid date)

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
            previous_close_yesterday = float(get_previous_close(f"^{symbol}", get_previous_date()))
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
    # Stock.objects.all().update(UPUsers = 0, DownUsers = 0)
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

def withdrawAborted(request, id):
    txn = WalletTxn.objects.get(ID = id)
    user = UserDetail.objects.get(User = txn.User)
    user.WalletBalance = user.WalletBalance - txn.Amount
    user.save()
    txn.TxnID = "N/A"
    txn.DateTime = datetime.now()
    txn.Status = "FAILED"
    txn.save()
    sendEmail("withdrawals@bullpov.com", txn.User.email, "Withdrawal Request Failed", normal_text_templates(txn.User.first_name, f"Your recent withdrawal request of ₹{txn.Amount} could not be processed. <br><br>Please review your account details and try again. If you need assistance, reply to this email or contact our support team."))
    return redirect("userWithdrawalRequests")

def updateTrends(request):
    gainer = str(request.GET["gainer"]).split("-")
    loser = str(request.GET["loser"]).split("-")
    volume = str(request.GET["volume"]).split("-")
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

