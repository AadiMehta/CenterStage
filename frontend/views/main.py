from django.shortcuts import redirect
from django.views.generic import TemplateView
from frontend.utils import get_user_from_token, is_authenticated


class HomeTemplateView(TemplateView):
    """
    Centerstage home page
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context

    def dispatch(self, request, *args, **kwargs):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return redirect('dashboard-lessons')

        return super(HomeTemplateView, self).dispatch(request, *args, **kwargs)


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
