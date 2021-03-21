import urllib
from django.conf import settings
from django.views.generic import TemplateView


class AccountConnectedTemplate(TemplateView):
    """
    This template is rendered on Zoom connect success
    to close the window and refresh the parent page
    """
    template_name = "zoom/zoom_auth_success.html"


class StudentOnboardStep1TemplateView(TemplateView):
    """
    After sign up the user is asked for following
    basic details:
        - Bio
        - Profile Image
    """
    template_name = "student/onboarding/step1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class OnboardStep1TemplateView(TemplateView):
    """
    After sign up the user is asked for following
    basic details:
        - Profession name
        - Bio
        - Custom Page name
    """
    template_name = "teacher/onboarding/step1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['site_name'] = settings.SITE_URL
        return context


class OnboardStep2TemplateView(TemplateView):
    """
    Onboarding step 2
    """
    template_name = "teacher/onboarding/step2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        teacher_accounts = {}
        accounts = self.request.user.accounts.all()
        payment_account = self.request.user.payment_account.all()
        if payment_account:
            payment_account = True
        else:
            payment_account = False
        for account in accounts:
            teacher_accounts[account.account_type] = account
        context.update({
            'user': self.request.user,
            'teacher_accounts': teacher_accounts,
            'payment_account': payment_account,
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
    template_name = "teacher/onboarding/step3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
