from django.conf import settings
from django.views.generic import TemplateView
from frontend.utils import get_user_from_token
from engine.models import LessonData
from engine.serializers import LessonSerializer
 

class DashboardAccountAlerts(TemplateView):
    """
    Dashboard Account Alerts
    """
    template_name = "dashboard/account/alerts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class DashboardAccountInfo(TemplateView):
    """
    Dashboard Account Info
    """
    template_name = "dashboard/account/info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        context['site_name'] = settings.SITE_URL
        return context


class DashboardAccountPayment(TemplateView):
    """
    Dashboard Account Payment
    """
    template_name = "dashboard/account/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class DashboardSchedulesPastSessions(TemplateView):
    """
    Dashboard Schedules Past Sessions
    """
    template_name = "dashboard/schedules/pastsessions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class DashboardSchedulesUpcomingSessions(TemplateView):
    """
    Dashboard Schedules Upcoming Sessions
    """
    template_name = "dashboard/schedules/upcoming.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class DashboardLessons(TemplateView):
    """
    Dashboard Lessons
    """
    template_name = "dashboard/lessons.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = LessonData.objects.all().order_by('-created_at')
        serializer = LessonSerializer(lessons, many=True)
        context['lessons'] = serializer.data
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class DashboardMessages(TemplateView):
    """
    Dashboard Messages
    """
    template_name = "dashboard/messages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context


class DashboardStatistics(TemplateView):
    """
    Dashboard Statistics
    """
    template_name = "dashboard/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context
