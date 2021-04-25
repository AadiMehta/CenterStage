from django import forms
from users.models import UserTypes
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import BadHeaderError, HttpResponse


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


class ZoomPolicyView(TemplateView):
    """
    Privacy Policy
    """
    template_name = "zoom.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class Faqs(TemplateView):
    """
    Faqs
    """
    template_name = "faq.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class ContactForm(forms.Form):
    name = forms.CharField(max_length=50)
    email_address = forms.EmailField(max_length=150)
    phone_no = forms.CharField(max_length=16)
    message = forms.CharField(widget=forms.Textarea, max_length=2000)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Centrestage Support Inquiry"
            body = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email_address'],
                'phone_no': form.cleaned_data['phone_no'],
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, 'support@centrestage.live', ['tanayjanakdesai@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("homepage")

    form = ContactForm()
    return render(request, "public/support_page.html", {'form': form})
