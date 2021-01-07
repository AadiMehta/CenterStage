import urllib
import os
from django.conf import settings
from django.views.generic import TemplateView
from frontend.utils import get_user_from_token


class HomeTemplateView(TemplateView):
    """
    Centerstag home page
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class TermsAndConditionsView(TemplateView):
    """
    Terms and Conditions
    """
    template_name = "terms-condition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context
