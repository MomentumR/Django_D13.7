from django.shortcuts import redirect
from django.urls import reverse


class VerifyEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.groups.filter(name='verified_users').exists():
            if request.path not in [reverse('verify_email'), reverse('account_logout'), reverse('resend_code')]:
                return redirect('verify_email')

        response = self.get_response(request)
        return response
