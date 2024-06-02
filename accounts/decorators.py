from django.shortcuts import redirect,reverse
from functools import wraps

from accounts.views import generate_verification_code, send_verification_code


def email_verification_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Kullanıcı giriş yapmamışsa login sayfasına yönlendir
        if not request.user.profile.isEmailVerified:

            send_verification_code(request.user, generate_verification_code())
            return redirect('verifyEmail')  # E-posta doğrulanmamışsa doğrulama sayfasına yönlendir
        return view_func(request, *args, **kwargs)
    return _wrapped_view
