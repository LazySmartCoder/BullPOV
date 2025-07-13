from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name = "HomePage"),
    path("about-us", aboutUs, name = "AboutUs"),
    path("signup", signup, name = "SignUP"),
    path("signin", signin, name = "SignIN"),
    path("register", register, name = "Register"),
    path("login", logIn, name = "Login"),
    path("signout", signout, name = "SignOut"),
    path("contact", contact, name = "Contact"),
    path("contact-save", contactSave, name = "ContactSave"),
    path("dashboard", dashboard, name = "Dashboard"),
    path("account", account, name = "Account"),
    # fu is forgot username
    path("fu", fu, name = "FU"),
    path("forgot-password", forgotpass, name = "ForgotPassword"),
    path("password-recovery-verification/<str:otp>", passRecoverVerify, name = "PasswordRecoverVerify"),
    # pr is password recovery
    path("pr/<str:otp>", pr, name = "PasswordRecovery"),
    path("forgot-username", forgotuser, name = "ForgotUsername"),
    # fp is forgot password
    path("fp", fp, name = "FP"),
    path("user-verification", userVerification, name = "UserVerification"),
    # vu is verify user
    path("vu", verifyUser, name = "VerifyUser"),
    path("market-data-updation", marketDataUpdation, name = "MarketDataUpdation"),
    path("search", search, name = "Search"),
    path("stock-preview/<str:symbol>", stockPreview, name = "StockPreview"),
    path("categories", categories, name = "Categories"),
    path("trade-history", tradeHistory, name = "TradeHistory"),
    path("trade-details/<str:symbol>", tradeDetails, name = "TradeDetails"),
    path("hit-order/<str:stock>", hitOrder, name = "HitOrder"),
    path("check-return-rate/<str:stock>", checkReturnRate, name = "CheckReturnRate"),
    path("update-profile", updateProfile, name = "UpdateProfile"),
    path("delete-acc", deleteAcc, name = "DeleteAcc"),
    path("password-change", passwordChange, name = "passwordChange"),
    path("change-email/<str:verify>", changeEmail, name = "ChangeEmail"),
    path("watch-list", watchList, name = "WatchList"),
    path("remove-watch-list/<str:stock>", removeWatchList, name = "RemoveWatchList"),
    path("add-watch-list/<str:stock>", addWatchList, name = "AddWatchList"),
]