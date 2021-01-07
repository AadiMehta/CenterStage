import urllib
import os
from django.conf import settings
from django.views.generic import TemplateView
from frontend.utils import get_user_from_token


class AccountConnectedTemplate(TemplateView):
    """
    This template is rendered on Zoom connect sucess
    to close the window and refresh the parent page
    """
    template_name = "zoom/zoom_auth_success.html"


class OnboardStep1TemplateView(TemplateView):
    """
    Onboarding step 1
    """
    template_name = "onboarding/step1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class OnboardStep2TemplateView(TemplateView):
    """
    Onboarding step 2
    """
    template_name = "onboarding/step2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            user = get_user_from_token(self.request.COOKIES.get('auth_token'))
            teacher_accounts = {}
            accounts = user.teacher_profile_data.accounts.all()
            for account in accounts:
                teacher_accounts[account.account_type] = account
            context.update({
                'user': user,
                'teacher_accounts': teacher_accounts,
                'zoom': {
                    'ZOOM_CLIENT_ID': settings.ZOOM_CLIENT_ID,
                    'ZOOM_REDIRECT_URL': urllib.parse.quote_plus(settings.ZOOM_REDIRECT_URL)
                }
            })
        return context


class OnboardStep3TemplateView(TemplateView):
    """
    Onboarding step 3
    """
    template_name = "onboarding/step3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context
