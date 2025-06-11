from django.db import models
from django.contrib.auth.models import User

class UserDetail(models.Model):
    User = models.ForeignKey(User, related_name="OtherUserDetails", on_delete=models.CASCADE)
    Newsletters = models.BooleanField(default=False)
    ForgotPasswordOTP = models.CharField(default="")
    PhoneNumber = models.CharField(default="")
    
    def __str__(self):
        return self.User.username