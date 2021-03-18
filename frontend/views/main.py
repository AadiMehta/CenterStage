from django.shortcuts import redirect
from django.views.generic import TemplateView
from users.models import UserTypes


class HomeTemplateView(TemplateView):
    """
    Centerstage home page
    """
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == UserTypes.STUDENT_USER:
                return redirect('student-dashboard-main')
            return redirect('dashboard-lessons')

        return super(HomeTemplateView, self).dispatch(request, *args, **kwargs)


class TermsAndConditionsView(TemplateView):
    """
    Terms and Conditions
    """
    template_name = "terms-condition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class PrivacyPolicyView(TemplateView):
    """
    Privacy Policy
    """
    template_name = "privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context
