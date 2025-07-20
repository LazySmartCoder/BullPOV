from django.urls import path
from BullPOVAdmin.views import *

urlpatterns = [
    path("/home", index, name = "AdminPage"),
    path("/update-stocks", updateStocks, name = "AllStocks"),
    path("/data-clean", dataClean, name = "DataClean"),
    path("/declare-results", declareResults, name = "DeclareResults"),
    path("/indice-update", indiceUpdate, name = "IndiceUpdate"),
]