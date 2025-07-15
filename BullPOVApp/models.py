from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Stock(models.Model):
    Name = models.CharField(default="")
    Logo = models.CharField(default="")
    Symbol = models.CharField(default="")
    Sector = models.CharField(default="")
    Description = models.CharField(default="", max_length=10000)
    CurrentPrice = models.FloatField(default=0)
    DayHigh = models.FloatField(default=0)
    DayLow = models.FloatField(default=0)
    OpeningPrice = models.FloatField(default=0)
    ClosingPrice = models.FloatField(default=0)
    PriceChange = models.FloatField(default=0)
    Volume = models.FloatField(default=0)
    MktCap = models.FloatField(default=0)
    PERatio = models.FloatField(default=0)
    DividendYield = models.FloatField(default=0)
    EPS = models.FloatField(default=0)
    DayLow = models.FloatField(default=0)
    DayHigh = models.FloatField(default=0)
    Nifty50 = models.BooleanField(default=False)
    TopGainer = models.BooleanField(default=False)
    TopLoser = models.BooleanField(default=False)
    LastUpdateTime = models.DateField(default=datetime.now())
    UPUsers = models.IntegerField(default=0)
    DownUsers = models.IntegerField(default=0)
    TotalUsers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.Name} | {self.Symbol}"

class UserDetail(models.Model):
    User = models.ForeignKey(User, related_name="OtherUserDetails", on_delete=models.CASCADE)
    ProfilePhoto = models.ImageField(upload_to='ProfilePhotos/', default='/default.png')
    Newsletters = models.BooleanField(default=False)
    OTPEmail = models.CharField(default="")
    OTPPhone = models.CharField(default="")
    PhoneNumber = models.CharField(default="")
    Country = models.CharField(default="India")
    VerifiedAccount = models.BooleanField(default=False)
    VerificationOTP = models.CharField(default="")
    Address = models.CharField(default="")
    UPI = models.CharField(default="")
    WalletBalance = models.FloatField(default=0)
    InvestedBalance = models.FloatField(default=0)
    Watchlist = models.ManyToManyField(Stock, blank=True, related_name='watchList')
    
    def __str__(self):
        return self.User.username

class Trade(models.Model):
    Trader = models.ForeignKey(User, related_name="TraderDetails", on_delete=models.CASCADE)
    Stock = models.ForeignKey(Stock, related_name="StockDetails", on_delete=models.CASCADE)
    Amount = models.FloatField(default=0)
    DateTime = models.CharField(default="")
    Prediction = models.BooleanField(default=None) # True means UP, False means Down
    ActiveStatus = models.BooleanField(default=False)
    Return = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Trader} | {self.Stock}"

class Contact(models.Model):
    Name = models.CharField(default="")
    Email = models.EmailField(default="")
    Subject = models.CharField(default="")
    Message = models.TextField(default="")

    def __str__(self):
        return self.Subject