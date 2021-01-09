import os
import urllib
import base64

from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import redirect
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
