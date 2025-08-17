from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Stock(models.Model):
    Name = models.CharField(default="")
    Logo = models.CharField()
    Symbol = models.CharField(default="", db_index=True)
    Sector = models.CharField(default="", db_index=True)
    Description = models.CharField(default="", max_length=10000)
    CurrentPrice = models.FloatField(default=0, db_index=True)
    OpeningPrice = models.FloatField(default=0, db_index=True)
    PreviousCloseToday = models.FloatField(default=0, db_index=True)
    PreviousCloseYesterday = models.FloatField(default=0, db_index=True)
    PriceChange = models.FloatField(default=0, db_index=True)
    Volume = models.FloatField(default=0, db_index=True)
    MktCap = models.FloatField(default=0, db_index=True)
    PERatio = models.FloatField(default=0)
    DividendYield = models.FloatField(default=0)
    EPS = models.FloatField(default=0)
    DayLow = models.FloatField(default=0)
    DayHigh = models.FloatField(default=0)
    Nifty50 = models.BooleanField(default=False, db_index=True)
    TopGainer = models.BooleanField(default=False, db_index=True)
    TopLoser = models.BooleanField(default=False, db_index=True)
    TopVolume = models.BooleanField(default=False, db_index=True)
    UPUsers = models.IntegerField(default=0, db_index=True)
    DownUsers = models.IntegerField(default=0, db_index=True)
    PlatformCut = models.FloatField(default=5)

    def __str__(self):
        return f"{self.Name} | {self.Symbol}"

class UserDetail(models.Model):
    User = models.ForeignKey(User, related_name="OtherUserDetails", on_delete=models.CASCADE)
    ProfilePhoto = models.ImageField(upload_to='ProfilePhotos/', default='/default.png')
    DOB = models.CharField(default="")
    Newsletters = models.BooleanField(default=False)
    OTPEmail = models.CharField(default="")
    OTPPhone = models.CharField(default="")
    PhoneNumber = models.CharField(default="")
    Country = models.CharField(default="India")
    VerifiedAccount = models.BooleanField(default=False)
    VerificationOTP = models.CharField(default="")
    Address = models.CharField(default="")
    WalletBalance = models.FloatField(default=0)
    InvestedBalance = models.FloatField(default=0)
    Watchlist = models.ManyToManyField(Stock, blank=True, related_name='watchList')
    
    def __str__(self):
        return self.User.username

class Trade(models.Model):
    TradeID = models.CharField(max_length=1000, default="")
    Trader = models.ForeignKey(User, related_name="TraderDetails", on_delete=models.CASCADE)
    Stock = models.ForeignKey(Stock, related_name="StockDetails", on_delete=models.CASCADE)
    Amount = models.FloatField(default=0)
    DateTime = models.CharField(default="")
    Prediction = models.BooleanField(default=None) # True means UP, False means Down
    ActiveStatus = models.BooleanField(default=False)
    Return = models.FloatField(default=0)
    Outcome = models.BooleanField(default=False) # False means Lose, True means Won!
    Receipt = models.CharField(default="")

    def __str__(self):
        return f"{self.Trader} | {self.Stock}"

class Contact(models.Model):
    Name = models.CharField(default="")
    Email = models.EmailField(default="")
    Subject = models.CharField(default="")
    Message = models.TextField(default="")
    DateTime = models.CharField(default="")

    def __str__(self):
        return self.Subject

class Samachaar(models.Model):
    Image = models.CharField(default="")
    Name = models.CharField(default="")
    Category = models.CharField(default="")
    Date = models.CharField(default="")
    Source = models.CharField(default="")
    Link = models.CharField(default="")

    def __str__(self):
        return f"{self.Name} | {self.Source}"

class WalletTxn(models.Model):
    # if the payment is done: SUCCESS
    # if the payment fails: FAILED
    # if users aborts: ABORTED
    # if status is pending: PENDING
    # if users cancels payment: CANCELLED
    ID = models.CharField(default="")
    User = models.ForeignKey(User, related_name="TxnDetails", on_delete=models.CASCADE)
    Amount = models.FloatField(default=0)
    Action = models.BooleanField(default=False) # True for deposit, and False for withdrawal
    OrderID = models.CharField(default="")
    TxnID = models.CharField(default="")
    Status = models.CharField(default="")
    WithdrawalUPI = models.CharField(default="")
    DateTime = models.CharField(default="")

    def __str__(self):
        return f"{self.User.username} | {self.Amount} | {self.Action} | {self.Status}"
