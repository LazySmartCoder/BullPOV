from django.urls import path
from .views import *

urlpatterns = [
    path("", adminIndex, name = "adminIndex"),
    path("update-indices", indiceUpdate, name = "indiceUpdate"),
    path("update-stocks", updateStocks, name = "updateStocks"),
    path("declare-results", declareResults, name = "declareResults"),
    path("close-trading", closeTrading, name = "closeTrading"),
    path("open-trading", openTrading, name = "openTrading"),
    path("data-maintainence", dataMaintainence, name = "dataMaintainence"),
    path("uwr", userWithdrawalRequests, name = "userWithdrawalRequests"),
    path("withdrawn/<str:id>", withdrawn, name = "withdrawn"),
    path("withdraw-aborted/<str:id>", withdrawAborted, name = "withdrawAborted"),
    path("update-trends", updateTrends, name = "updateTrends"),
    path("platform-cut", platformCut, name = "platformCut"),
]