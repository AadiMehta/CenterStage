import urllib
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect

from users.models import TeacherProfile
from engine.models import LessonData


class TeacherPageView(TemplateView):
    template_name = "public/teacherpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return redirect('homepage')
        context['user'] = self.request.user
        context['teacher'] = self.request.user.teacher_profile_data
        context['lessons'] = LessonData.objects.filter(creator=self.request.user.teacher_profile_data)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('homepage')
        teacher = TeacherProfile.objects.filter(user=self.request.user).first()
        if not teacher:
            return redirect('homepage')
        return super(TeacherPageView, self).dispatch(request, *args, **kwargs)



class LessonPageView(TemplateView):
    template_name = "public/teacherpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
