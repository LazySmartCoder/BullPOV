from django.shortcuts import redirect
from django.urls import resolve
from .models import UserDetail
from django.urls import reverse
from .views import sendEmail
from .emailTemplates import *

class OTPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        user = request.user
        if request.path in [reverse("SignOut"), reverse("VerifyUser")]:
            return self.get_response(request)
        elif not request.path == reverse('UserVerification'):
            if user.is_authenticated and (UserDetail.objects.get(User = user).VerifiedAccount == False):
                userdet = UserDetail.objects.get(User = user)
                sendEmail("no-reply@bullpov.com", request.user.email, f"Email Verification OTP - {userdet.VerificationOTP}", otp_verification_template(request.user.first_name, str(userdet.VerificationOTP)))
                return redirect(reverse('UserVerification'))

        return self.get_response(request)
