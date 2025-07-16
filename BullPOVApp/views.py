from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.db.models import Q
import string
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import locale
from .MarketFeatures import *

# Some important functions and variables
site_url = "localhost:8000"
locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')

def convert_to_crores(amount):
    try:
        # Convert to float to support decimals
        amount = float(amount)
        crores = amount / 1e7  # 1 crore = 1 crore = 1 * 10^7
        formatted = locale.format_string("%.2f", crores, grouping=True)
        return f"₹{formatted} Cr"
    except Exception as e:
        return f"Error: {e}"

def is_valid_password(s):
    if len(s) < 8:
        return False
    has_letter = any(c.isalpha() for c in s)
    has_digit = any(c.isdigit() for c in s)
    has_special = any(c in string.punctuation for c in s)
    return has_letter and has_digit and has_special

def sendEmail(sender, receiver, subject, message):
    sender_email = sender
    sender_password = google_app_password
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
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

# logical codes starts here
def index(request):
    topt = {}
    topTraded = Stock.objects.filter(Nifty50 = True)
    for i in topTraded:
        topt[i.Symbol] = i.UPUsers + i.DownUsers
    topTraded = sorted(topt, key=topt.get, reverse=True)[:3]
    topTraded = Stock.objects.filter(Symbol__in=topTraded)
    return render(request, "index.html", {"stocks" : topTraded})

def aboutUs(request):
    return render(request, "about-us.html")

def signin(request):
    return render(request, "sign-in.html")

def signup(request):
    return render(request, "sign-up.html")

def register(request):
    if request.method == "POST":
       fname = request.POST["fname"]
       lname = request.POST["lname"]
       email = request.POST["email"]
       phone = request.POST["phone"]
       username = str(request.POST["username"]).lower()
       pass1 = request.POST["pass1"]
       pass2 = request.POST["pass2"]
       if pass1 != pass2:
           messages.warning(request, "Passwords do not match. Please try again.")
           return redirect("SignUP")
       if User.objects.filter(username=username).exists():
           messages.warning(request, "This username is already registered with us. Kindly use the suggestion.")
           usern = f"{fname[0:4]}{lname[0:4]}{random.randint(100, 999)}"
           return render(request, "sign-up.html", {"username" : usern})
       if User.objects.filter(email=email).exists():
           messages.warning(request, "An user with this email is already registered with us.")
           return redirect("SignUP")
       if UserDetail.objects.filter(PhoneNumber = phone).exists():
           messages.warning(request, "An user with this phone number is already registered with us.")
           return redirect("SignUP")
       if is_valid_password(pass1) == False:
           messages.warning(request, "Password must be at least 8 characters long and include letters, numbers, and special characters.")
           return redirect("SignUP")
       creating_user = User.objects.create_user(username=username, password=pass1)
       creating_user.email = email
       creating_user.first_name = f"{fname} {lname}"
       creating_user.save()
       authenticating = authenticate(request, username=username, password=pass1)
       if authenticating is not None:
           login(request, authenticating)
           veriotp = random.randint(100000, 999999)
           userdet = UserDetail(User = request.user, Newsletters = ("newsletter" in request.POST), PhoneNumber = phone, VerificationOTP = veriotp)
           userdet.save()
           sendEmail("no-reply@bullpov.com", email, "Verify your email", f"Your otp for email verfication is: {veriotp}")
           messages.success(request, "Congrats!!! Your BullPOV account has been created successfully. Please verify yourself.")
       else:
           messages.warning(request, "Something went wrong. Please try again later.")
           return redirect("SignUP")
       return redirect("UserVerification")
    return redirect("ErrorPage")

def logIn(request):
    if request.method == "POST":
        username = str(request.POST["username"]).lower()
        password = request.POST["password"]
        remember = request.POST.get("remember", "off")
        authenticating = authenticate(username=username, password=password)
        if authenticating is not None:
            login(request, authenticating)
            if remember == "off":
                request.session.set_expiry(0)
            messages.success(request, "Signed IN")
        else:
            messages.warning(request, "Please fill in all fields correctly")
            return redirect("SignIN")
        return redirect("Dashboard")
    return redirect("ErrorPage")

def forgotuser(request):
    return render(request, "forgot-username.html")

def fu(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(email = email).exists():
            username = User.objects.get(email = email).username
            messages.success(request, "Your username has been displayed.")
            return render(request, "sign-in.html", {"username" : username})
        else:
            messages.warning(request, "No user found with this email.")
        return redirect("ForgotUsername")

def forgotpass(request):
    return render(request, "forgot-password.html")

def fp(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(email = email).exists():
            userdet = User.objects.get(email = email)
            save_otp = UserDetail.objects.get(User = userdet)
            forgotp = random.randint(1000, 9999)
            save_otp.OTPEmail = str(forgotp)
            save_otp.save()
            sendEmail("no-reply@bullpov.com", email, "Password Recovery", f"tap this link - https://bullpov.com/password-recovery-verification/{email}-{forgotp}")
            messages.success(request, "A password recovery email has been sent to your email.")
            return redirect("HomePage")
        else:
            messages.warning(request, "No user found with this email.")
        return redirect("ForgotPassword")
    
def passRecoverVerify(request, otp):
    email = str(otp).split("-")[0]
    forotp = str(otp).split("-")[1]
    if User.objects.filter(email = email).exists():
        user = User.objects.get(email = email)
        if UserDetail.objects.get(User = user).OTPEmail == forotp:
            messages.success(request, "Create New Password.")
            return render(request, "new-password.html", {"email" : email, "otp" : forotp})
        else:
            messages.warning(request, "Password Recovery failed.")
    else:
        messages.warning(request, "Password Recovery failed.")
    return redirect("HomePage")

def pr(request, otp):
    email = str(otp).split("-")[0]
    forotp = str(otp).split("-")[1]
    if request.method == "POST":
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        print(pass1)
        if pass1 != pass2:
           messages.warning(request, "Passwords do not match. Please try again.")
           return render(request, "new-password.html", {"email" : email, "otp" : forotp})
        if is_valid_password(pass1) == False:
           messages.warning(request, "Password must be at least 8 characters long and include letters, numbers, and special characters.")
           return render(request, "new-password.html", {"email" : email, "otp" : forotp})
        user = User.objects.get(email = email)
        user.set_password(pass1)
        user.save()
        sendEmail("no-reply@bullpov.com", email, "Password Recovered", "Your password has been changed.")
        messages.success(request, "Password changed. You may SignIN now.")
        return redirect("SignIN")
        
def signout(request):
    logout(request)
    messages.success(request, "Signed Out")
    return redirect("HomePage")
        
def userVerification(request):
    return render(request, "user-verification.html")

def verifyUser(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        if str(otp) == UserDetail.objects.get(User = request.user).VerificationOTP:
            userdet = UserDetail.objects.get(User = request.user)
            userdet.VerifiedAccount = True
            userdet.save()
            messages.success(request, "Account verified successfully.")
        else:
            messages.warning(request, "Please enter the correct OTP.")
        return redirect("HomePage")

def ErrorPage(request, exception):
    # This is for handler 404
    return render(request, "error-page.html")

def ErrorOccured(request):
    # This is for handler 500
    return render(request, "error-page.html")

def contact(request):
    return render(request, "contact.html")

def contactSave(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        subject = request.POST["subject"]
        message = request.POST["message"]
        conSave = Contact(Name = name, Email = email, Subject = subject, Message = message)
        conSave.save()
        messages.success(request, "We have received your message / feedback. We will revert back via email.")
        return redirect("Contact")


# calculation and hit order starts
def checkReturnRate(request, stock):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    share = Stock.objects.get(Symbol = str(stock).split("-")[0])
    if Trade.objects.filter(Trader = request.user, Stock = share, ActiveStatus = True).exists():
        messages.success(request, "You can only place one order in a complete trading cycle.")
        return redirect(f"/trade-details/{str(stock).split("-")[0]}")
    predict = False
    if str(stock).split("-")[1] == "UP":
        predict = True
    if request.method == "POST":
        amt = int(request.POST["amount"])

        # up party data
        totalAmtup = 0
        retrieve_up = Trade.objects.filter(Stock = share, Prediction = True, ActiveStatus = True)
        for i in retrieve_up:
            totalAmtup += i.Amount
        
        # down party data
        totalAmtdown = 0
        retrieve_down = Trade.objects.filter(Stock = share, Prediction = False, ActiveStatus = True)
        for i in retrieve_down:
            totalAmtdown += i.Amount

        def percentage_to_multiplier(percent):
            multiplier = (percent / 100) + 1
            return round(multiplier, 2)
        if predict == True:
            remAmt = totalAmtup + amt
            returnPercentage = amt / remAmt * 100
            if totalAmtdown != 0:
                userReturn = returnPercentage / 100 * totalAmtdown
            else:
                userReturn = returnPercentage / 100 * 500
            returnRate = percentage_to_multiplier(userReturn / amt * 100)
        if predict == False:
            remAmt = totalAmtdown + amt
            returnPercentage = amt / remAmt * 100
            if totalAmtup != 0:
                userReturn = returnPercentage / 100 * totalAmtup
            else:
                userReturn = returnPercentage / 100 * 500
            returnRate = percentage_to_multiplier(userReturn / amt * 100)
        return render(request, "check-return-rate.html", {"rate" : returnRate, "return" : userReturn + amt, "stock" : share, "predict" : str(stock).split("-")[1], "amt" : amt})

def hitOrder(request, stock):
    predict = False
    if str(stock).split("-")[1] == "UP":
        predict = True
    if request.method == "POST":
        amt = float(str(stock).split("-")[2])
        share = Stock.objects.get(Symbol = str(stock).split("-")[0])
        if Trade.objects.filter(Trader = request.user, Stock = share, ActiveStatus = True).exists():
            messages.success(request, "You can only place one order in a complete trading cycle.")
            return redirect(f"/trade-details/{str(stock).split("-")[0]}")
        user = UserDetail.objects.get(User = request.user)
        user.WalletBalance = user.WalletBalance - amt
        user.InvestedBalance = user.InvestedBalance + amt
        user.save()

        # up party data
        totalAmtup = 0
        retrieve_up = Trade.objects.filter(Stock = share, Prediction = True, ActiveStatus = True)
        for i in retrieve_up:
            totalAmtup += i.Amount
        
        # down party data
        totalAmtdown = 0
        retrieve_down = Trade.objects.filter(Stock = share, Prediction = False, ActiveStatus = True)
        for i in retrieve_down:
            totalAmtdown += i.Amount

        if predict == True:
            share.UPUsers = share.UPUsers + 1
            share.save()
            remAmt = totalAmtup + amt
            returnPercentage = amt / remAmt * 100
            if totalAmtdown != 0:
                userReturn = returnPercentage / 100 * totalAmtdown
            else:
                print("OK")
                userReturn = returnPercentage / 100 * 500
                defTrade = Trade(Trader = User.objects.get(username = "anni"), Stock = share, Amount = 500, DateTime = datetime.now(), Prediction = False, ActiveStatus = True, Return = userReturn)
                defTrade.save()
        if predict == False:
            share.DownUsers = share.DownUsers + 1
            share.save()
            remAmt = totalAmtdown + amt
            returnPercentage = amt / remAmt * 100
            if totalAmtup != 0:
                userReturn = returnPercentage / 100 * totalAmtup
            else:
                print("OK")
                userReturn = returnPercentage / 100 * 500
                defTrade = Trade(Trader = User.objects.get(username = "anni"), Stock = share, Amount = 500, DateTime = datetime.now(), Prediction = True, ActiveStatus = True, Return = userReturn)
                defTrade.save()
        initTrade = Trade(Trader = request.user, Stock = share, Amount = amt, DateTime = datetime.now(), Prediction = predict, ActiveStatus = True, Return = userReturn)
        initTrade.save()
        return redirect(f"/trade-details/{share.Symbol}")
# calculations and hit orders ends    


# accounts management starts
def account(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    userdet = UserDetail.objects.get(User = request.user)
    return render(request, "user-profile.html", {"user" : userdet, "url" : site_url})

def passwordChange(request):
    if request.method == "POST":
        old = request.POST["old"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        if pass1 != pass2:
            messages.warning(request, "Password mismatch.")
            return redirect("/account")
        if not is_valid_password(pass1):
            messages.warning(request, "Enter a strong password.")
            return redirect("/account")
        if request.user.check_password(old):
            request.user.set_password(pass1)
            request.user.save()
            messages.success(request, "Your password has been changed.")
        else:
            messages.warning(request, 'Enter correct old password. If you forgot, logout and go to "Forgot Password" to change.')
        return redirect("HomePage")

def deleteAcc(request):
    if request.method == "POST":
        pwd = request.POST["pwd"]
        if request.user.check_password(pwd):
            request.user.delete()
            messages.warning(request, "Account Deleted.")
            # send an email here
            return redirect("HomePage")
        else:
            messages.warning(request, "Incorrect Password.")
        return redirect("/account")

def updateProfile(request):
    if request.method == "POST":
        pfp = request.FILES.get('pfp')
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        address = request.POST["address"]
        password = request.POST["password"]
        user = request.user
        if user.check_password(password):
            userdet = UserDetail.objects.get(User = user)
            user.first_name = name
            if user.email != email:
                cotp = random.randint(1000, 9999)
                userdet.OTPEmail = cotp
                userdet.save()
                sendEmail("no-reply@bullpov.com", email, "Change email", f"Your email will be changed as soon as you click this link: https://bullpov.com/change-email/{email}-{cotp}")
                messages.success(request, "Your email will be changed as soon as you verify yourself.")
            userdet.PhoneNumber = phone
            userdet.Address = address
            userdet.ProfilePhoto = pfp
            user.save()
            userdet.save()
            sendEmail("no-reply@bullpov.com", email, "Profile Updated", "Your profile has been updated.")
            messages.success(request, "Profile has been updated.")
        else:
            messages.warning(request, "Enter correct password.")
        return redirect("/account")

def changeEmail(request, verify):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    user = request.user
    userdet = UserDetail.objects.get(User = user)
    if userdet.OTPEmail == str(verify).split("-")[1]:
        user.email = str(verify).split("-")[0]
        user.save()
        messages.success(request, "Email has been changed.")
    else:
        messages.warning(request, "Email not changed.")
    return redirect("HomePage")
# accounts management ends

# displaying market data in different paths starts
def dashboard(request):
    if request.user.is_authenticated == False:
        return redirect("SignIN")
    # indice data list access for the scroller
    indice_results = {}
    for i in Stock.objects.filter(Symbol__in=['^NSEI', '^BSESN', '^NSEBANK', '^CNXIT', '^NSEMDCP50']):
        change_percent = ((i.CurrentPrice - i.OpeningPrice) / i.OpeningPrice) * 100
        trend = "up" if change_percent > 0 else "down" if change_percent < 0 else "no"
        indice_results[i.Name] = [i.CurrentPrice, i.PriceChange, trend]
    
    # top data to be displayed
    topGainers = Stock.objects.filter(TopGainer = True)[:4]
    topLosers = Stock.objects.filter(TopLoser = True)[:4]

    topv = {}
    topVolumes = Stock.objects.filter(Nifty50 = True)
    for i in topVolumes:
        topv[i.Symbol] = i.Volume
    topVolumes = sorted(topv, key=topv.get, reverse=True)[:4]
    topVolumes = Stock.objects.filter(Symbol__in=topVolumes)

    topt = {}
    topTraded = Stock.objects.filter(Nifty50 = True)
    for i in topTraded:
        topt[i.Symbol] = i.UPUsers + i.DownUsers
    topTraded = sorted(topt, key=topt.get, reverse=True)[:4]
    topTraded = Stock.objects.filter(Symbol__in=topTraded)

    topm = {}
    topMktCap = Stock.objects.filter(Nifty50 = True)
    for i in topMktCap:
        topm[i.Symbol] = float(str(i.MktCap).replace(",", "").replace(" Crores", ""))
    topMktCap = sorted(topm, key=topm.get, reverse=True)[:20]
    topMktCap = Stock.objects.filter(Symbol__in=topMktCap)

    # getting user trades data to be displayed
    usertradesdata = []
    usertrades = Trade.objects.filter(Trader = request.user, ActiveStatus = True)[:4]
    for i in usertrades:
        usertradesdata.append(i.Stock)
    if len(usertradesdata) == 0:
        usertradesdata = None

    return render(request, "dashboard.html", {"data" : indice_results, "topGainers" : topGainers, "topLosers" : topLosers, "topVolumes" : topVolumes, "topTraded" : topTraded, "topMktCap" : topMktCap, "userTrades" : usertradesdata})

def search(request):
    search_text = request.GET["search"]
    results = Stock.objects.filter(
    Q(Name__icontains=search_text) | Q(Symbol__icontains=search_text)
)
    return render(request, "search.html", {"search" : results, "searchText" : search_text, "count" : results.count()})

def stockPreview(request, symbol):
    stock = Stock.objects.get(Symbol = symbol)
    trades = Trade.objects.filter(Stock = stock, Prediction = True, ActiveStatus = True)
    totalamtup = 0
    for i in trades:
        totalamtup += i.Amount
    trades = Trade.objects.filter(Stock = stock, Prediction = False, ActiveStatus = True)
    totalamtdown = 0
    for i in trades:
        totalamtdown += i.Amount
    if (stock.CurrentPrice - stock.ClosingPrice) > 0:
        change = True
    else:
        change = False
    try:
        upPercent = totalamtup / (totalamtdown + totalamtup) * 100
        downPercent = totalamtdown / (totalamtdown + totalamtup) * 100
    except ZeroDivisionError:
        upPercent = 50
        downPercent = 50
    stockDesc = get_stock_description(stock.Name)
    if request.user.is_authenticated:
        user = UserDetail.objects.get(User = request.user)
        return render(request, "stock-preview.html", {"stock" : stock, "change" : change, "user" : user, "up" : upPercent, "down" : downPercent, "desc" : stockDesc, "totalamt" : totalamtdown + totalamtup})
    else:
        return render(request, "stock-preview.html", {"stock" : stock, "change" : change, "up" : upPercent, "down" : downPercent, "desc" : stockDesc, "totalamt" : totalamtdown + totalamtup})

def categories(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    # top data to be displayed
    topGainers = Stock.objects.filter(TopGainer = True)[:4]
    topLosers = Stock.objects.filter(TopLoser = True)[:4]

    topv = {}
    topVolumes = Stock.objects.filter(Nifty50 = True)
    for i in topVolumes:
        topv[i.Symbol] = i.Volume
    topVolumes = sorted(topv, key=topv.get, reverse=True)[:4]
    topVolumes = Stock.objects.filter(Symbol__in=topVolumes)

    topt = {}
    topTraded = Stock.objects.filter(Nifty50 = True)
    for i in topTraded:
        topt[i.Symbol] = i.UPUsers + i.DownUsers
    topTraded = sorted(topt, key=topt.get, reverse=True)[:4]
    topTraded = Stock.objects.filter(Symbol__in=topTraded)

    # getting user trades data to be displayed
    usertradesdata = []
    usertrades = Trade.objects.filter(Trader = request.user)[:4]
    for i in usertrades:
        usertradesdata.append(i.Stock)

    # Tag each stock with its category and combine into one list
    categories = []

    for stock in topGainers:
        categories.append({"type": "top-gainers", "stock": stock})

    for stock in topLosers:
        categories.append({"type": "top-losers", "stock": stock})

    for stock in topVolumes:
        categories.append({"type": "top-volumes", "stock": stock})

    for stock in topTraded:
        categories.append({"type": "top-traded", "stock": stock})

    for stock in usertradesdata:
        categories.append({"type": "user-trades", "stock": stock})

    return render(request, "category.html", {"categories" : categories})

def tradeHistory(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    usertradesdata = []
    usertrades = Trade.objects.filter(Trader = request.user)
    for i in usertrades:
        usertradesdata.append(i.Stock)
    return render(request, "trade-history.html", {"history" : zip(usertradesdata, usertrades)})

def tradeDetails(request, symbol):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    stock = Stock.objects.get(Symbol = symbol)
    trader = Trade.objects.get(Trader = request.user, Stock = stock)
    user = UserDetail.objects.get(User = request.user)
    if trader.Prediction:
        predict = "UP"
    else:
        predict = "DOWN"
    
    return render(request, "trade-details.html", {"stock" : stock, "trade" : trader, "user" : user, "totalamt" : trader.Return + trader.Amount, "predict" : predict})
# displaying market data in different paths ends


# watchlist functions starts
def watchList(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    userlist = UserDetail.objects.get(User = request.user)
    watchlist = userlist.Watchlist.all()
    return render(request, "watch-list.html", {"watch" : watchlist})

def addWatchList(request, stock):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    userlist = UserDetail.objects.get(User = request.user)
    userlist.Watchlist.add(Stock.objects.get(Symbol = stock))
    userlist.save()
    messages.success(request, "Watch List Updated.")
    return redirect(f"/stock-preview/{stock}")

def removeWatchList(request, stock):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    userlist = UserDetail.objects.get(User = request.user)
    userlist.Watchlist.remove(Stock.objects.get(Symbol = stock))
    userlist.save()
    messages.success(request, "Watch List Updated.")
    return redirect("WatchList")
# watchlist functions ends


# wallet functions starts
def wallet(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    userdet = UserDetail.objects.get(User = request.user)
    return render(request, "wallet.html", {"user" : userdet, "suggest" : userdet.WalletBalance * 0.6})

def addMoney(request):
    if request.method == "POST":
        amt = request.POST["amount"]
        userdet = UserDetail.objects.get(User = request.user)
        userdet.WalletBalance = userdet.WalletBalance + int(amt)
        userdet.save()
        messages.success(request, "Money added.")
        return redirect("Wallet")

def withdrawMoney(request):
    if request.method == "POST":
        amt = int(request.POST["amount"])
        userdet = UserDetail.objects.get(User = request.user)
        if amt > userdet.WalletBalance:
            messages.warning(request, "Insufficient balance.")
            return redirect("Wallet")
        userdet.WalletBalance = userdet.WalletBalance - amt
        userdet.save()
        messages.success(request, "Money withdrawn.")
        return redirect("Wallet")
# wallet functions ends



def downloadApp(request):
    return render(request, "download-app.html")

def eLearning(request):
    return render(request, "e-learning.html")

def marketInfo(request):
    return render(request, "market-info.html")