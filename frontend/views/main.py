from django.shortcuts import redirect
from django.views.generic import TemplateView
from frontend.utils.auth import get_user_from_token, is_authenticated
from users.models import UserTypes


class HomeTemplateView(TemplateView):
    """
    Centerstage home page
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES and is_authenticated(self.request.COOKIES.get('auth_token')):
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context

    def dispatch(self, request, *args, **kwargs):
        user = self.get_user()
        if user:
            if user.user_type == UserTypes.STUDENT_USER:
                return redirect('student-dashboard-main')
            return redirect('dashboard-lessons')

        return super(HomeTemplateView, self).dispatch(request, *args, **kwargs)

    def get_user(self):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return get_user_from_token(self.request.COOKIES.get('auth_token'))
        else:
            return False


class TermsAndConditionsView(TemplateView):
    """
    Terms and Conditions
    """
    template_name = "terms-condition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES and is_authenticated(self.request.COOKIES.get('auth_token')):
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class PrivacyPolicyView(TemplateView):
    """
    Privacy Policy
    """
    template_name = "privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES and is_authenticated(self.request.COOKIES.get('auth_token')):
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context
