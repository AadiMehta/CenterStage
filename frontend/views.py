import urllib
import os
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from users.models import User


# Temporary Function for get and set user
def get_user_from_token(auth_token):
    try:
        user_id = Token.objects.get(key=auth_token).user_id
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass


class HomeTemplateView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class TermsAndConditionsView(TemplateView):
    template_name = "terms-condition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class OnboardStep1TemplateView(TemplateView):
    """
    """
    template_name = "onboardingstage1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class AccountConnectedTemplate(TemplateView):
    """

    """
    template_name = "zoom_auth_success.html"


class OnboardStep2TemplateView(TemplateView):
    template_name = "onboardingstage2.html"

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
    template_name = "onboardingstage3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context
