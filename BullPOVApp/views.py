from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from .models import *
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils.encoding import force_str
import uuid
import string
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils import timezone
from datetime import timedelta
import random
from .emailTemplates import *
import locale
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .credentials import *
from reportlab.lib.pagesizes import A4
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.shortcuts import HttpResponse
from django.db import connections, transaction
import sqlite3
from pathlib import Path
from cashfree_pg.api_client import Cashfree
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
import hmac, hashlib, json
from django.conf import settings
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
Cashfree.XClientId = "1032514dc2c30325fe7444306234152301"
Cashfree.XClientSecret = "cfsk_ma_prod_c7c76f38c9ef7134f84ba1df857e0874_e16973e8"
Cashfree.XEnvironment = Cashfree.PRODUCTION
x_api_version = "2023-08-01"

# Some important functions and variables
site_url = "localhost:8000"
locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os

def generate_transaction_receipt_pdf(amount, action, order_id, txn_id, status, username, name, email, date):
    try:
        os.makedirs("assets/Receipts", exist_ok=True)
        filename = f"assets/Receipts/Transaction/{username}-{txn_id}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Background
        c.setFillColor(colors.HexColor("#F4F6F8"))  # Light grey
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Card container
        card_margin = 40
        card_top = height - 60
        card_bottom = 80
        c.setFillColor(colors.white)
        c.roundRect(card_margin, card_bottom, width - 2*card_margin, card_top - card_bottom, 10, fill=1)

        # Logo
        logo_path = "assets/Logo.png"
        if os.path.exists(logo_path):
            c.drawImage(logo_path, card_margin + 15, card_top - 70, width=50, height=50, mask='auto')

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#1F4E79"))
        c.drawString(card_margin + 75, card_top - 50, "BullPOV - Transaction Receipt")

        # Subtitle
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.grey)
        c.drawString(card_margin + 75, card_top - 65, f"Issued by BullPOV EdTech Company | Txn ID: {txn_id}")

        # Divider
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(card_margin + 15, card_top - 80, width - card_margin - 15, card_top - 80)

        # Two-column layout
        left_x = card_margin + 30
        right_x = width / 2 + 10
        y = card_top - 110
        spacing = 24

        left_data = [
            ("Order ID", order_id),
            ("Transaction ID", txn_id),
            ("Date", date),
            ("Status", status),
            ("Action", action),
        ]

        right_data = [
            ("Name", name),
            ("Username", username),
            ("Email", email),
            ("Amount", f"{amount:.2f} Rs"),
            ("Net Paid", f"{amount:.2f} Rs"),
        ]

        # Left column
        for label, value in left_data:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#1F4E79"))
            c.drawString(left_x, y, f"{label}")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(left_x + 130, y, str(value))
            y -= spacing

        # Right column
        y = card_top - 110
        for label, value in right_data:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#1F4E79"))
            c.drawString(right_x, y, f"{label}")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(right_x + 130, y, str(value))
            y -= spacing

        # Note
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.gray)
        c.drawString(card_margin + 30, card_bottom + 30, "Note: This receipt is auto-generated and does not require a signature.")

        # Footer
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#1F4E79"))
        c.drawCentredString(width / 2, 50, "Generated by BullPOV | www.bullpov.com")

        c.save()
        return None

    except Exception as e:
        print("PDF Generation Failed:", e)
        return None


def get_global_index_data():
    import yfinance as yf
    # Top 6 indices with their Yahoo Finance symbols
    indices = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^NSEI": "Nifty 50",
        "^BSESN": "Sensex",
        "^IXIC": "NASDAQ",
        "^FTSE": "FTSE 100"
    }

    # Dictionary to store result
    index_data = {}

    for symbol, name in indices.items():
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="2d")  # Ensure we get at least two days to calculate change

        if not data.empty and len(data) >= 2:
            ltp = round(data['Close'].iloc[-1], 2)
            prev_close = round(data['Close'].iloc[-2], 2)
            change = round(ltp - prev_close, 2)
            percent_change = round((change / prev_close) * 100, 2) if prev_close != 0 else 0.0

            index_data[symbol] = {
                "name": name,
                "ltp": ltp,
                "change": change,
                "percent_change": percent_change
            }
        else:
            index_data[symbol] = {
                "name": name,
                "ltp": None,
                "change": None,
                "percent_change": None
            }

    return index_data

def generate_trade_bill_pdf(amount, username, name, tid, email, date, stock, prediction):
    try:
        filename = f"assets/Receipts/Trade/{username}-{tid}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Background
        c.setFillColor(colors.HexColor("#F4F6F8"))  # Light grey background
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # White card container
        card_margin = 40
        card_top = height - 60
        card_bottom = 80
        c.setFillColor(colors.white)
        c.roundRect(card_margin, card_bottom, width - 2*card_margin, card_top - card_bottom, 10, fill=1)

        # Company Logo
        logo_path = "assets/Logo.png"
        if os.path.exists(logo_path):
            c.drawImage(logo_path, card_margin + 15, card_top - 70, width=50, height=50, mask='auto')

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#1F4E79"))
        c.drawString(card_margin + 75, card_top - 50, "BullPOV - Trade Receipt")

        # Subtitle
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.grey)
        c.drawString(card_margin + 75, card_top - 65, "Issued by BullPOV EdTech Company | Receipt No: " + tid)

        # Divider line
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(card_margin + 15, card_top - 80, width - card_margin - 15, card_top - 80)

        # Two-column info layout
        left_x = card_margin + 30
        right_x = width / 2 + 10
        y = card_top - 110
        spacing = 24

        left_data = [
            ("Trade ID", tid),
            ("Trade Date", date),
            ("Status", "SUCCESS"),
            ("Trader Name", name),
            ("Username", username),
            ("Email", email),
        ]

        right_data = [
            ("Prediction", prediction),
            ("Stock", stock),
            ("Trade Amount", f"{amount:.2f} Rs"),
            ("Platform Fee", f"0 Rupees"),
            ("Net Paid", f"{amount:.2f} Rs"),
        ]

        # Left column
        for label, value in left_data:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#1F4E79"))
            c.drawString(left_x, y, f"{label}")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(left_x + 130, y, str(value))
            y -= spacing

        y = card_top - 110
        # Right column
        for label, value in right_data:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#1F4E79"))
            c.drawString(right_x, y, f"{label}")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(right_x + 130, y, str(value))
            y -= spacing

        # Note at bottom
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.gray)
        c.drawString(card_margin + 30, card_bottom + 30, "Note: This receipt is auto-generated and does not require a signature.")

        # Footer Branding
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#1F4E79"))
        c.drawCentredString(width / 2, 50, "Generated by BullPOV | www.bullpov.com")

        c.save()
        return None

    except Exception as e:
        return None

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
    if request.user.is_authenticated == False:
        return render(request, "sign-in.html")
    return redirect("ErrorPage")

def signup(request):
    if request.user.is_authenticated == False:
        return render(request, "sign-up.html")
    return redirect("ErrorPage")

def register(request):
    if request.method == "POST":
       fname = request.POST["fname"]
       lname = request.POST["lname"]
       email = request.POST["email"]
       phone = request.POST["phone"]
       username = str(request.POST["username"]).lower()
       dob = request.POST["dob"]
       address = request.POST["address"]
       pass1 = request.POST["pass1"]
       pass2 = request.POST["pass2"]
       if not (date.today() - date.fromisoformat(dob)).days >= 14 * 365:
           messages.warning(request, "You are too young for this.")
           return redirect("SignUP")
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
           userdet = UserDetail(User = request.user, DOB = dob, Newsletters = ("newsletter" in request.POST), PhoneNumber = phone, VerificationOTP = veriotp, Address = address)
           userdet.save()
           sendEmail("no-reply@bullpov.com", email, f"Email Verification OTP - {veriotp}", otp_verification_template(fname, str(veriotp)))
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
            messages.warning(request, "Make sure all fields are filled out correctly.")
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
            messages.success(request, "Your username has been revealed.")
            return render(request, "sign-in.html", {"username" : username})
        else:
            messages.warning(request, "No account found with this email address.")
        return redirect("ForgotUsername")

def forgotpass(request):
    return render(request, "forgot-password.html")

def fp(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(email = email).exists():
            userdet = User.objects.get(email = email)
            name = userdet.first_name
            save_otp = UserDetail.objects.get(User = userdet)
            forgotp = random.randint(1000, 9999)
            save_otp.OTPEmail = str(forgotp)
            save_otp.save()
            sendEmail("no-reply@bullpov.com", email, "BullPOV Password Recovery", normal_text_templates(name, f"We received a request to reset your password for your account at BullPOV. To proceed, please click the link below:<br>https://bullpov.com/password-recovery-verification/{email}-{forgotp}"))
            messages.success(request, "A password recovery link has been sent to your email.")
            return redirect("HomePage")
        else:
            messages.warning(request, "No account found with this email address.")
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
            messages.warning(request, "Password recovery failed. Please try again.")
    else:
        messages.warning(request, "Password recovery failed. Please try again.")
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
        name = user.first_name
        user.set_password(pass1)
        user.save()
        sendEmail("no-reply@bullpov.com", email, "Your Password Has Been Successfully Reset", normal_text_templates(name, "Just a quick note to let you know that your password was successfully reset. If you requested this, you’re all set, you can now log in with your new password. Your security is our priority. Stay safe and informed."))
        messages.success(request, "Your password has been changed. You can now sign in.")
        return redirect("SignIN")
        
def signout(request):
    logout(request)
    messages.success(request, "Signed Out")
    return redirect("HomePage")
        
def userVerification(request):
    if (timezone.now() - request.user.date_joined >= timedelta(minutes=5)) and (UserDetail.objects.get(User=request.user).VerifiedAccount == False):
        request.user.delete()
        messages.success(request, "OTP Expired. SignUP again.")
        return redirect("HomePage")
    return render(request, "user-verification.html")

def verifyUser(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        if str(otp) == UserDetail.objects.get(User = request.user).VerificationOTP:
            userdet = UserDetail.objects.get(User = request.user)
            userdet.VerifiedAccount = True
            userdet.save()
            sendEmail("no-reply@bullpov.com", request.user.email, "Welcome to BullPOV!!", normal_text_templates(request.user.first_name, """Welcome to BullPOV, India’s first skill-based stock trend prediction platform!<br>
We’re excited to have you on board.<br>
Here, you can study real market data, predict tomorrow’s stock trends, and win real money based on your skills. No luck, no gambling, just your knowledge and smart thinking.
<br>Start spotting trends after 4:30 PM                                                                                                         
<br>Predict Up or Down before 9:00 AM                                                                                                    
<br>Get results by 4:30 PM next day                                                                                                 
<br>Learn. Play. Earn.<br>
Let’s turn your market instinct into real rewards.
<br>Happy Trading!"""))
            messages.success(request, "Your account has been successfully verified.")
        else:
            messages.warning(request, "Invalid OTP. Please try again.")
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
        conSave = Contact(Name = name, Email = email, Subject = subject, Message = message, DateTime = datetime.now())
        conSave.save()
        messages.success(request, "Thank you for your message. We'll get back to you via email shortly.")
        return redirect("Contact")


# calculation and hit order starts
def checkReturnRate(request, stock):
    if User.objects.get(username = "anni").last_name == "close":
        messages.warning(request, "Trading Pool is closed.")
        return redirect("HomePage")
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    share = Stock.objects.get(Symbol = str(stock).split("-")[0])
    predict = False
    if str(stock).split("-")[1] == "UP":
        predict = True
    if request.method == "POST":
        amt = int(request.POST["amount"])
        user = UserDetail.objects.get(User = request.user)
        if amt > user.WalletBalance:
            messages.success(request, "Deposit Money to continue.")
            return redirect(f"/wallet")

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
            returnRate = percentage_to_multiplier(returnPercentage)
            userReturn = amt * float(returnRate)
        if predict == False:
            remAmt = totalAmtdown + amt
            returnPercentage = amt / remAmt * 100
            returnRate = percentage_to_multiplier(returnPercentage)
            userReturn = amt * float(returnRate)
        return render(request, "check-return-rate.html", {"rate" : returnRate, "return" : userReturn, "stock" : share, "predict" : str(stock).split("-")[1], "amt" : amt})

def hitOrder(request, stock):
    if request.user.is_authenticated:
        if User.objects.get(username = "anni").last_name == "close":
            messages.warning(request, "Trading Pool is Closed.")
            return redirect("HomePage")
        predict = False
        if str(stock).split("-")[1] == "UP":
            predict = True
        amt = float(str(stock).split("-")[2])
        user = UserDetail.objects.get(User = request.user)
        share = Stock.objects.get(Symbol = str(stock).split("-")[0])
        if Trade.objects.filter(Trader = request.user, Stock = share, ActiveStatus = True).exists():
            messages.success(request, "Only one trade/stock is allowed per trading cycle.")
            return redirect(f"/trade-details/{str(stock).split("-")[0]}/{Trade.objects.get(Trader = request.user, Stock = share, ActiveStatus = True).TradeID}")
        if amt > user.WalletBalance:
            messages.success(request, "Deposit Money to continue.")
            return redirect(f"/wallet")
        user.WalletBalance = user.WalletBalance - amt
        user.InvestedBalance = user.InvestedBalance + amt
        user.save()
        if predict == True:
            share.UPUsers = share.UPUsers + 1
            share.save()
        if predict == False:
            share.DownUsers = share.DownUsers + 1
            share.save()
        initTrade = Trade(TradeID = Trade.objects.all().count(), Trader = request.user, Stock = share, Amount = amt, DateTime = datetime.now(), Prediction = predict, ActiveStatus = True, Receipt = f"{request.user.username}-{Trade.objects.all().count()}")
        sendEmail("no-reply@bullpov.com", request.user.email, f"{str(stock).split("-")[0]} trade placed on BullPOV!!", normal_text_templates(request.user.first_name, f"Your order has been successfully placed! <br><br>Stock: {share.Name}<br>Amount: ₹{amt}<br>Trade Receipt:- https://bullpov.com/trade-receipt/{Trade.objects.all().count()}<br><br>Now sit back and hold tight, results will be declared soon. <br>We wish you the best of luck!"))
        initTrade.save()
        return redirect(f"/trade-details/{share.Symbol}/{Trade.objects.get(Trader = request.user, Stock = share, ActiveStatus = True).TradeID}")
# calculations and hit orders ends    


# accounts management starts
def account(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "Please SignIN first.")
        return redirect("SignIN")
    userdet = UserDetail.objects.get(User = request.user)
    return render(request, "user-profile.html", {"user" : userdet, "url" : site_url})

def passwordChange(request):
    if request.method == "POST":
        old = request.POST["old"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        if pass1 != pass2:
            messages.warning(request, "Passwords do not match. Please try again.")
            return redirect("/account")
        if not is_valid_password(pass1):
            messages.warning(request, "Enter a stronger password to continue.")
            return redirect("/account")
        if request.user.check_password(old):
            name = request.user.first_name
            request.user.set_password(pass1)
            request.user.save()
            sendEmail("no-reply@bullpov.com", request.user.email, "BullPOV Password Changed", normal_text_templates(name, "This is a quick confirmation that your BullPOV account password has been successfully changed. Stay safe."))
            messages.success(request, "Your password has been changed. SignIN Now!")
        else:
            messages.warning(request, 'The old password you entered is incorrect. To reset it, log out and click on "Forgot Password".')
        return redirect("HomePage")

def deleteAcc(request):
    if request.method == "POST":
        pwd = request.POST["pwd"]
        if UserDetail.objects.get(User = request.user).WalletBalance == 0 and UserDetail.objects.get(User = request.user).InvestedBalance == 0:
            if request.user.check_password(pwd):
                name = request.user.first_name
                request.user.delete()
                messages.warning(request, "Account has been scheduled for deletion.")
                sendEmail("no-reply@bullpov.com", request.user.email, "We're sorry to see you go", normal_text_templates(name, "We noticed you've deleted your account, and we're truly sorry to see you leave. If there’s anything we could’ve done better or any feedback you'd like to share, we’d love to hear from you, your input helps us improve. You’re always welcome back anytime. If you decide to return, just log in or create a new account — we’ll be here for you. Wishing you the very best ahead."))
                return redirect("HomePage")
            else:
                messages.warning(request, "Incorrect Password.")
            return redirect("/account")
        messages.warning(request, "Kindly settle your wallet before account deletion.")
        return redirect("Wallet")

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
                sendEmail("no-reply@bullpov.com", email, "Verify your new email address to complete the update", normal_text_templates(request.user.first_name, f"You recently requested to update your email address on BullPOV. To confirm this change and keep your account secure, please verify your new email by clicking the link below:<br>https://bullpov.com/change-email/{email}-{cotp} <br><br>Thanks for helping us keep your account safe."))
                messages.success(request, "Email Address change pending. Complete verification to proceed.")
            userdet.PhoneNumber = phone
            userdet.Address = address
            userdet.ProfilePhoto = pfp
            user.save()
            userdet.save()
            sendEmail("no-reply@bullpov.com", email, "Your profile has been successfully updated", normal_text_templates(request.user.first_name, "Just letting you know, your profile information was updated successfully. We’ve saved the changes and everything looks good on our end. Thanks for staying with us."))
            messages.success(request, "Your profile has been updated.")
        else:
            messages.warning(request, "Incorrect Password.")
        return redirect("/account")

def changeEmail(request, verify):
    if request.user.is_authenticated == False:
        messages.warning(request, "Please SignIN first.")
        return redirect("SignIN")
    user = request.user
    userdet = UserDetail.objects.get(User = user)
    if userdet.OTPEmail == str(verify).split("-")[1]:
        user.email = str(verify).split("-")[0]
        user.save()
        sendEmail("no-reply@bullpov.com", request.user.email, "Your email has been successfully updated", normal_text_templates(request.user.first_name, f"We wanted to let you know that the email address linked to your BullPOV account has been successfully updated. <br><br>New Email: {str(verify).split("-")[0]} <br><br>If you made this change, you're all set! Thanks for being a part of BullPOV."))
        messages.success(request, "Email Address has been changed.")
    else:
        messages.warning(request, "Email Address Updation Failed.")
    return redirect("HomePage")
# accounts management ends

# displaying market data in different paths starts
def dashboard(request):
    if request.user.is_authenticated == False:
        return redirect("SignIN")
    # indice data list access for the scroller
    indice_results = {}
    for i in Stock.objects.filter(Symbol__in=['NSEI', 'BSESN', 'NSEBANK', 'CNXIT', 'NSEMDCP50']):
        if i.OpeningPrice != 0:
            change_percent = ((i.CurrentPrice - i.OpeningPrice) / i.OpeningPrice) * 100
        else:
            change_percent = 0

        trend = "up" if change_percent > 0 else "down" if change_percent < 0 else "no"

        indice_results[i.Name] = {
            'price': i.CurrentPrice,
            'change': change_percent,
            'trend': trend,
        }

    
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
    usertrades = Trade.objects.filter(Trader = request.user, ActiveStatus = True)[:4:-1]
    for i in usertrades:
        usertradesdata.append(i.Stock)
    if len(usertradesdata) == 0:
        usertradesdata = None    
    if len(usertrades) != 0:
        return render(request, "dashboard.html", {"data" : indice_results, "topGainers" : topGainers, "topLosers" : topLosers, "topVolumes" : topVolumes, "topTraded" : topTraded, "topMktCap" : topMktCap, "userTrades" : zip(usertradesdata, usertrades), "topIndices" : Stock.objects.filter(Symbol__in=['NSEI', 'BSESN', 'NSEBANK', 'CNXIT', 'NSEMDCP50'])})
    else:
        return render(request, "dashboard.html", {"data" : indice_results, "topGainers" : topGainers, "topLosers" : topLosers, "topVolumes" : topVolumes, "topTraded" : topTraded, "topMktCap" : topMktCap, "topIndices" : Stock.objects.filter(Symbol__in=['NSEI', 'BSESN', 'NSEBANK', 'CNXIT', 'NSEMDCP50'])})


def search(request):
    search_text = request.GET["search"]
    results = Stock.objects.filter(
    Q(Name__icontains=search_text) | Q(Symbol__icontains=search_text) | Q(Sector__icontains=search_text)
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
    def percentage_to_multiplier(percent):
        multiplier = (percent / 100) + 1
        return round(multiplier, 2)
    for i in trades:
        totalamtdown += i.Amount
    if (stock.CurrentPrice - stock.PreviousCloseToday) > 0:
        change = True
    else:
        change = False
    try:
        upPercent = totalamtup / (totalamtdown + totalamtup) * 100
        downPercent = totalamtdown / (totalamtdown + totalamtup) * 100
    except ZeroDivisionError:
        upPercent = 50
        downPercent = 50
    if request.user.is_authenticated:
        user = UserDetail.objects.get(User = request.user)
        return render(request, "stock-preview.html", {"stock" : stock, "change" : change, "user" : user, "up" : percentage_to_multiplier(upPercent), "down" : percentage_to_multiplier(downPercent), "totalamt" : totalamtdown + totalamtup})
    else:
        return render(request, "stock-preview.html", {"stock" : stock, "change" : change, "up" : percentage_to_multiplier(upPercent), "down" : percentage_to_multiplier(downPercent), "totalamt" : totalamtdown + totalamtup})

def categories(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "Please SignIN first.")
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
    usertrades = Trade.objects.filter(Trader = request.user, ActiveStatus = True)[::-1]
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
    
    for stock in Stock.objects.filter(Symbol__in=['NSEI', 'BSESN', 'NSEBANK', 'CNXIT', 'NSEMDCP50']):
        categories.append({"type": "top-indices", "stock": stock})

    return render(request, "category.html", {"categories" : categories})

def tradeHistory(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    usertradesdata = []
    usertrades = Trade.objects.filter(Trader = request.user)
    for i in usertrades:
        usertradesdata.append(i.Stock)
    return render(request, "trade-history.html", {"history" : zip(usertradesdata[::-1], usertrades[::-1])})

def tradeDetails(request, symbol, tid):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    stock = Stock.objects.get(Symbol = symbol)
    trader = Trade.objects.get(TradeID = tid, Trader = request.user, Stock = stock)
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
        messages.warning(request, "Please SignIN first.")
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
    messages.success(request, "Watchlist Updated.")
    return redirect(f"/watch-list")

def removeWatchList(request, stock):
    if request.user.is_authenticated == False:
        messages.warning(request, "SignIN first.")
        return redirect("SignIN")
    userlist = UserDetail.objects.get(User = request.user)
    userlist.Watchlist.remove(Stock.objects.get(Symbol = stock))
    userlist.save()
    messages.success(request, "Watchlist Updated.")
    return redirect("WatchList")
# watchlist functions ends

# wallet functions starts
def wallet(request):
    if request.user.is_authenticated == False:
        messages.warning(request, "Please SignIN first.")
        return redirect("SignIN")
    txn = WalletTxn.objects.filter(User = request.user, Action = True, Status = "PENDING")
    for t in txn:
        t.Status = "CANCELLED"
        t.save()
    userdet = UserDetail.objects.get(User = request.user)
    return render(request, "wallet.html", {"user" : userdet, "suggest" : userdet.WalletBalance * 0.6})

def create_order(id, amt, phone):
    customerDetails = CustomerDetails(customer_id=id, customer_phone=phone)

    # 👇 Corrected: Placing return_url inside order_meta
    createOrderRequest = CreateOrderRequest(
        order_amount=amt,
        order_currency="INR",
        customer_details=customerDetails,
        order_meta={
            "return_url": "https://00d9fcb315ae.ngrok-free.app/payment-status?order_id={order_id}"
        }
    )

    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        if hasattr(api_response, "data") and hasattr(api_response.data, "payment_session_id"):
            return [api_response.data.payment_session_id, api_response.data.order_id]
        else:
            return None
    except Exception as e:
        return None

def addMoney(request):
    if request.method == "POST":
        amt = float(request.POST["amount"])
        if amt + float(UserDetail.objects.get(User = request.user).WalletBalance) > 10000:
            messages.warning(request, "Max Deposit Limit is ₹10,000/-")
            return redirect("Wallet")
        session_id = create_order(id = f"{request.user.username}{random.randint(100000, 999999)}", amt = amt, phone = "6355853038")
        txn = WalletTxn(ID = WalletTxn.objects.all().count(),User = request.user, Amount = amt, Action = True, OrderID = session_id[1], Status = "PENDING")
        txn.save()
        return render(request, "checkout.html", {"id" : session_id[0], "amt" : amt})
    
def check_payment_status(request):
    order_id = request.GET.get('order_id')
    try:
        api_response = Cashfree().PGFetchOrder(x_api_version, order_id, None)
        if api_response.data.order_status == "PAID":
            txn = WalletTxn.objects.get(OrderID = order_id)
            txn.TxnID = api_response.data.cf_order_id
            txn.Status = "SUCCESS"
            txn.DateTime = datetime.now()
            txn.save()
            userdet = UserDetail.objects.get(User = request.user)
            userdet.WalletBalance = userdet.WalletBalance + txn.Amount
            userdet.save()
            sendEmail("no-reply@bullpov.com", request.user.email, "Money Successfully Credited to Your BullPOV Wallet!", normal_text_templates(request.user.first_name, f"Great news! Your deposit has been successfully credited to your BullPOV wallet. <br><br>Deposited Amount: ₹{txn.Amount}<br>Current Balance: ₹{float(round(int(userdet.WalletBalance), 2))}<br><br>You can now use this amount to place trades on BullPOV. Happy Trading!"))
            messages.success(request, f"₹{txn.Amount} Credited to your Wallet")
        else:
            messages.warning(request, "Deposit Failed")
        return redirect("Wallet")
    except Exception as e:
        print(e)
        messages.warning(request, "Deposit Aborted")
        return redirect("Wallet")

def withdrawMoney(request):
    if request.method == "POST":
        amt = float(request.POST["amount"])
        upi = request.POST["upi"]
        userdet = UserDetail.objects.get(User = request.user)
        if amt > userdet.WalletBalance:
            messages.warning(request, "Insufficient Balance.")
            return redirect("Wallet")
        txn = WalletTxn(ID = WalletTxn.objects.all().count(), User = request.user, Amount = amt, Action = False, OrderID = f"BullPOV_{random.randint(10000, 99999)}", Status = "PENDING", WithdrawalUPI = upi, DateTime = datetime.now())
        txn.save()
        sendEmail("no-reply@bullpov.com", request.user.email, "Withdrawal Request Successfully Initiated!", normal_text_templates(request.user.first_name, f"Your withdrawal request has been successfully initiated, and the amount is on its way to your deposit account. <br><br>Withdrawn Amount: ₹{amt}<br>Current Balance: ₹{float(round(int(userdet.WalletBalance), 2))}<br><br>Expected Credit Time: Upto 7 business days. <br>If you face any delays or have questions, feel free to reach out to our support team. <br>Happy Trading!"))
        messages.success(request, "Withdrawal Request Initiated")
        return redirect("Wallet")
    
def walletTxnHistory(request):
    txn = WalletTxn.objects.filter(User = request.user, Action = True, Status = "PENDING")
    for t in txn:
        t.Status = "CANCELLED"
        t.save()
    txn = WalletTxn.objects.filter(User = request.user)
    paginator = Paginator(txn, 10)
    page = request.GET.get('page', '1')
    try:
        page_number = int(page)
        if page_number < 1:
            raise ValueError
    except (TypeError, ValueError):
        page_number = 1  # Default to page 1 on error

    try:
        page_txn = paginator.page(page_number)
    except EmptyPage:
        page_txn = paginator.page(paginator.num_pages)
    return render(request, "txn-history.html", {"txn" : page_txn})

def refundTxn(request, oid):
    txn = WalletTxn.objects.get(OrderID = oid)
    is_within_5_min = (datetime.now() - txn.DateTime) <= timedelta(minutes=5)
    if is_within_5_min == False:
        return redirect("HomePage")
    url = f"https://api.cashfree.com/pg/orders/{oid}"

    payload = {
        "refund_amount": txn.Amount,
        "refund_id": str(random.randint(100000, 999999))
    }
    headers = {
        "x-client-id": "1032514dc2c30325fe7444306234152301",
        "x-client-secret": "cfsk_ma_prod_c7c76f38c9ef7134f84ba1df857e0874_e16973e8",
        "x-api-version": "2025-01-01",
        "Content-Type": "application/json"
    }
    ctxn = WalletTxn(ID = WalletTxn.objects.all().count(), User = txn.User, Amount = txn.Amount, Action = False, OrderID = str(random.randint(100000, 999999)), TxnID = str(random.randint(100000, 999999)), Status = "SUCCESS", DateTime = datetime.now())
    ctxn.save()
    response = requests.post(url, json=payload, headers=headers)
    messages.success(request, f"Refund of ₹{txn.Amount} initiated")
    return redirect("Wallet")
# wallet functions ends

def downloadApp(request):
    return render(request, "download-app.html")

def eLearning(request):
    return render(request, "e-learning.html")

def samachaar(request):
    return render(request, "samachaar.html", {"index_data" : get_global_index_data(), "news" : Samachaar.objects.all()[:10:-1]})

def explore(request):
    stocks = Stock.objects.all()
    paginator = Paginator(stocks, 9)
    page = request.GET.get('page', '1')
    try:
        page_number = int(page)
        if page_number < 1:
            raise ValueError
    except (TypeError, ValueError):
        page_number = 1  # Default to page 1 on error

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, "explore.html", {'page_obj': page_obj})

def tac(request):
    return render(request, "tac.html")

def privacyPolicy(request):
    return render(request, "privacy-policy.html")

def tradeReceipt(request, tid):
    trade = Trade.objects.get(TradeID = tid)
    prediction = "UP"
    if trade.Prediction == False:
        prediction = "DOWN"
    generate_trade_bill_pdf(trade.Amount, trade.Trader.username, trade.Trader.first_name, tid, trade.Trader.email, datetime.now().date(), trade.Stock.Symbol, prediction)
    return redirect(f"/assets/Receipts/Trade/{trade.Trader.username}-{tid}.pdf")

def txnReceipt(request, id):
    txn = WalletTxn.objects.get(ID = id)
    action = "DEPOSIT"
    if txn.Action == False:
        action = "WITHDRAW"
    generate_transaction_receipt_pdf(txn.Amount, action, txn.OrderID, txn.TxnID, txn.Status, txn.User.username, txn.User.first_name, txn.User.email, str(txn.DateTime)[:10])
    return redirect(f"/assets/Receipts/Transaction/{txn.User.username}-{id}.pdf")