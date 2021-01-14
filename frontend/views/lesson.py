import os
import urllib
import base64

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import redirect, render
from django.core.cache import cache
from formtools.wizard.views import SessionWizardView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend.forms.lesson import LessonCreateFormStep1, LessonCreateFormStep2, LessonCreateFormStep3, \
    LessonCreateFormStep4, LessonCreateFormPreview
from frontend.utils import get_user_from_token


class LessonCreateStep1TemplateView(TemplateView):
    """
    Lesson Creation step 1
    """
    template_name = "lesson/step1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class LessonCreateStep2TemplateView(TemplateView):
    """
    Lesson Creation step 2
    """
    template_name = "lesson/step2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class LessonCreateStep3TemplateView(TemplateView):
    """
    Lesson Creation step 3
    """
    template_name = "lesson/step3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class LessonCreateStep4TemplateView(TemplateView):
    """
    Lesson Creation step 4
    """
    template_name = "lesson/step4.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class LessonCreatePreviewTemplateView(TemplateView):
    """
    Lesson Creation Preview
    """
    template_name = "lesson/preview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class LessonCreateWizard(SessionWizardView):
    TEMPLATES = {
        "step1": "lesson/step1.html",
        "step2": "lesson/step2.html",
        "step3": "lesson/step3.html",
        "step4": "lesson/step4.html",
        "preview": "lesson/preview.html",
    }

    FORMS = [
        # ("step1", LessonCreateFormStep1),
        # ("step2", LessonCreateFormStep2),
        ("step3", LessonCreateFormStep3),
        ("step4", LessonCreateFormStep4),
        ("preview", LessonCreateFormPreview),
    ]

    def get_context_data(self, form, **kwargs):
        print(form)
        print(kwargs)
        print( self.get_all_cleaned_data())
        context = super(LessonCreateWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'preview':
            context.update({'form_data': self.get_all_cleaned_data()})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = [form.cleaned_data for form in form_list]
        return render(self.request, 'lesson/done.html', {
            'form_data': data,
        })
        # return HttpResponseRedirect(reverse("lesson-creation-preview"))