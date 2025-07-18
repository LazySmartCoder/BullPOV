from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name = "AdminPage"),
    path("/update-stocks", update_all_stocks, name = "AllStocks"),
    path("/keep_top_500_by_market_cap", keep_top_500_by_market_cap, name = "keep_top_500_by_market_cap"),
    path("/declare", declareResults, name = "DeclareResults"),
]