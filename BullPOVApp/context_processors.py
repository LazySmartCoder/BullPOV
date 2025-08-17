from .models import *

def global_data(request):
    return {
        "walletbal": UserDetail.objects.get(User = request.user).WalletBalance,
    }
