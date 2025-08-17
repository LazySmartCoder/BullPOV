from .models import *

def global_data(request):
    if request.user.is_authenticated:
        return {
            "walletbal": UserDetail.objects.get(User = request.user).WalletBalance,
        }
    return {}
