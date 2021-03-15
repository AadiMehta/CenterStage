import urllib
import pytz
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.views.generic import TemplateView
from engine.models import LessonData, LessonSlots, LessonStatuses
from engine.serializers import LessonSerializer, LessonSlotSerializer


class DashboardAccountAlerts(TemplateView):
    """
    Dashboard Account Alerts
    """
    template_name = "teacher/dashboard/account/alerts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class DashboardAccountInfo(TemplateView):
    """
    Dashboard Account Info
    """
    template_name = "teacher/dashboard/account/info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        teacher_accounts = {}
        accounts = self.request.user.accounts.all()
        for account in accounts:
            teacher_accounts[account.account_type] = account
        context.update({
            'user': self.request.user,
            'teacher_accounts': teacher_accounts,
            'BASE_URL': settings.BASE_URL,
            'zoom': {
                'ZOOM_CLIENT_ID': settings.ZOOM_CLIENT_ID,
                'ZOOM_REDIRECT_URL': urllib.parse.quote_plus(settings.ZOOM_REDIRECT_URL)
            }
        })
        context['site_name'] = settings.SITE_URL
        return context


class DashboardAccountPayment(TemplateView):
    """
    Dashboard Account Payment
    """
    template_name = "teacher/dashboard/account/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class DashboardSchedulesPastSessions(TemplateView):
    """
    Dashboard Schedules Past Sessions
    """
    template_name = "teacher/dashboard/schedules/pastsessions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tz_now = timezone.now().astimezone(pytz.UTC)
        lesson_slots = LessonSlots.objects.filter(
            Q(lesson_from__lte=tz_now) | Q(lesson_to__lte=tz_now),
            lesson__status=LessonStatuses.ACTIVE,
            creator=self.request.user.teacher_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id')
        serializer = LessonSlotSerializer(lesson_slots, many=True)
        context['lessons_slots'] = serializer.data
        context['user'] = self.request.user
        return context


class DashboardSchedulesUpcomingSessions(TemplateView):
    """
    Dashboard Schedules Upcoming Sessions
    """
    template_name = "teacher/dashboard/schedules/upcoming.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tz_now = timezone.now().astimezone(pytz.UTC)
        lesson_slots = LessonSlots.objects.filter(
            Q(lesson_from__gte=tz_now) | Q(lesson_to__lte=tz_now),
            lesson__status=LessonStatuses.ACTIVE,
            creator=self.request.user.teacher_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id')
        serializer = LessonSlotSerializer(lesson_slots, many=True)
        context['lessons_slots'] = serializer.data
        context['user'] = self.request.user
        return context


class DashboardLessons(TemplateView):
    """
    Dashboard Lessons
    """
    template_name = "teacher/dashboard/lessons.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = LessonData.objects.filter(creator=self.request.user.teacher_profile_data).order_by('-created_at')
        serializer = LessonSerializer(lessons, many=True)
        context['lessons'] = serializer.data
        context['user'] = self.request.user
        return context


class DashboardMessages(TemplateView):
    """
    Dashboard Messages
    """
    template_name = "teacher/dashboard/messages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class DashboardStatistics(TemplateView):
    """
    Dashboard Statistics
    """
    template_name = "teacher/dashboard/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class DashboardStudents(TemplateView):
    """
    Dashboard Students
    """
    template_name = "teacher/dashboard/students.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
