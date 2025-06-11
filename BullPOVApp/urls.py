from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name = "HomePage"),
    path("signup", signup, name = "SignUP"),
    path("signin", signin, name = "SignIN"),
    path("register", register, name = "Register"),
    path("login", logIn, name = "Login"),
    path("signout", signout, name = "SignOut"),
    path("contact", contact, name = "Contact"),
    path("dashboard", dashboard, name = "Dashboard"),
    path("account", account, name = "Account"),
    path("fu", fu, name = "FU"),
    path("forgot-password", forgotpass, name = "ForgotPassword"),
    path("password-recovery-verification/<str:otp>", passRecoverVerify, name = "PasswordRecoverVerify"),
    path("pr/<str:otp>", pr, name = "PasswordRecovery"),
    path("forgot-username", forgotuser, name = "ForgotUsername"),
    path("fp", fp, name = "FP"),
]
