import urllib
from django.conf import settings
from django.views.generic import TemplateView


class SignupTemplateView(TemplateView):
    """
    Signup
    """
    template_name = "auth/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LoginTemplateView(TemplateView):
    """
    Login
    """
    template_name = "auth/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OtpTemplateView(TemplateView):
    """
    OTP
    """
    template_name = "auth/otp.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
