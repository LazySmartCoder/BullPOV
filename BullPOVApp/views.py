from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from .models import *
from django.contrib import messages
import string
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import random

# Some important functions
def is_valid_password(s):
    if len(s) < 8:
        return False
    has_letter = any(c.isalpha() for c in s)
    has_digit = any(c.isdigit() for c in s)
    has_special = any(c in string.punctuation for c in s)
    return has_letter and has_digit and has_special

def sendEmail(receiver, subject, message):
    sender_email = "no-reply@bullpov.com"
    sender_password = "nblzxvfbndpzumzn"
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        return None
    except Exception as e:
        print(f"Error sending email: {e}")


# BullPOV Code
def index(request):
    return render(request, "index.html")

def signin(request):
    return render(request, "sign-in.html")

def signup(request):
    return render(request, "sign-up.html")

def register(request):
    if request.method == "POST":
       fname = request.POST["fname"]
       lname = request.POST["lname"]
       email = request.POST["email"]
       username = request.POST["username"]
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
       if is_valid_password(pass1) == False:
           messages.warning(request, "Password must be at least 8 characters long and include letters, numbers, and special characters.")
           return redirect("SignUP")
       creating_user = User.objects.create_user(username=str(username).lower(), password=pass1)
       creating_user.email = email
       creating_user.first_name = f"{fname} {lname}"
       creating_user.save()
       authenticating = authenticate(request, username=username, password=pass1)
       if authenticating is not None:
           login(request, authenticating)
           userdet = UserDetail(User = request.user, Newsletters = ("newsletter" in request.POST))
           userdet.save()
           messages.success(request, "Congrats!!! Your BullPOV account has been created successfully. Please verify your phone number.")
       else:
           messages.warning(request, "Something went wrong. Please try again later.")
           return redirect("SignUP")
       return redirect("HomePage")
    return redirect("ErrorPage")

def logIn(request):
    if request.method == "POST":
        username = str(request.POST["username"]).lower()
        password = request.POST["password"]
        remember = request.POST["remember"]
        authenticating = authenticate(username=username, password=password)
        if authenticating is not None:
            login(request, authenticating)
            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
            messages.success(request, "Signed IN")
        else:
            messages.warning(request, "Please fill in all fields correctly")
            return redirect("SignIN")
        return redirect("HomePage")
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
            save_otp.ForgotPasswordOTP = str(forgotp)
            save_otp.save()
            # sendEmail(email, "Password Recovery", f"tap this link - https://bullpov.com/password-recovery/{email}-{forgotp}")
            messages.success(request, "A password recovery email has been sent to your email.")
        else:
            messages.warning(request, "No user found with this email.")
        return redirect("ForgotPassword")
    
def passRecoverVerify(request, otp):
    email = str(otp).split("-")[0]
    forotp = str(otp).split("-")[1]
    if User.objects.filter(email = email).exists():
        user = User.objects.get(email = email)
        if UserDetail.objects.get(User = user).ForgotPasswordOTP == forotp:
            messages.success(request, "Create New Password.")
            return render(request, "new-password.html", {"email" : email, "otp" : forotp})
        else:
            messages.warning(request, "Password Recovery failed.")
    else:
        messages.warning(request, "Password Recovery failed.")
    return redirect("ForgotPassword")

def pr(request, otp):
    email = str(otp).split("-")[0]
    forotp = str(otp).split("-")[1]
    if request.method == "POST":
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        if pass1 != pass2:
           messages.warning(request, "Passwords do not match. Please try again.")
           return render(request, "new-password.html", {"email" : email, "otp" : forotp})
        if is_valid_password(pass1) == False:
           messages.warning(request, "Password must be at least 8 characters long and include letters, numbers, and special characters.")
           return render(request, "new-password.html", {"email" : email, "otp" : forotp})
        user = User.objects.get(email = email)
        user.set_password("pass1")
        user.save()
        messages.success(request, "Password changed. You may SignIN now.")
        return redirect("SignIN")
        
    

def signout(request):
    logout(request)
    messages.success(request, "Signed Out")
    return redirect("HomePage")

def DeleteAccount(request):
    if request.method == "POST":
        password = request.POST["password"]
        if check_password(password, request.user.password):
            user = User.objects.get(username = request.user)
            user.delete()
            user.save()
            messages.success(request, "Your account has been successfully deleted. Never come back...")
            return redirect("HomePage")
        else:
            messages.warning(request, "Please enter the correct password.")
            return redirect("UserProfile")
    return redirect("ErrorPage")

def userprofile(request):
    return render(request, "user-profile.html")

def profileupdate(request):
    if request.method == "POST":
        if check_password(request.POST["password"], request.user.password):
            name = request.POST["name"]
            email = request.POST["email"]
            user = User.objects.get(username = request.user)
            user.first_name = name
            user.email = user.username = email
            user.save()
            messages.success(request, "Your profile has been successfully updated.")
        else:
            messages.warning(request, "Please enter the correct password.")
        return redirect("UserProfile")
    return redirect("ErrorPage")

def passwordchange(request):
    if request.method == "POST":
        password = request.POST["pass"]
        newpass1 = request.POST["newpass1"]
        newpass2 = request.POST["newpass2"]
        if (newpass1 == newpass2) and check_password(password, request.user.password):
            user = User.objects.get(username = request.user)
            user.set_password(newpass2)
            user.save()
            logout(request)
            messages.success(request, "Your password has been updated sucessfully.")
            return redirect("HomePage")
        else:
            messages.warning(request, "Something went wrong.")
            return redirect("UserProfile")

def ErrorPage(request, exception):
    # This is for handler 404
    return render(request, "error page.html")

def ErrorOccured(request):
    # This is for handler 500
    return render(request, "error page.html")

def contact(request):
    return render(request, "contact.html")

def dashboard(request):
    return render(request, "dashboard.html")

def account(request):
    return render(request, "account.html")