from django.shortcuts import redirect
from django.urls import resolve
from .models import UserDetail
from django.urls import reverse

class OTPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        user = request.user
        if request.path in [reverse("SignOut"), reverse("VerifyUser")]:
            return self.get_response(request)
        elif not request.path == reverse('UserVerification'):
            if user.is_authenticated and (UserDetail.objects.get(User = user).VerifiedAccount == False):
                return redirect(reverse('UserVerification'))

        return self.get_response(request)
