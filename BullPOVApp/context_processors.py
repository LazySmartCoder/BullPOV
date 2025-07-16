from .models import UserDetail

def globalWatchlist(request):
    if not request.user.is_authenticated:
        return {}
    watchlist = UserDetail.objects.get(User = request.user).Watchlist.all()
    return {'watchlist': watchlist[:3], "count" : watchlist.count()}