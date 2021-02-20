import urllib
import pytz
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.views.generic import TemplateView
from engine.models import LessonData, LessonSlots, LessonStatuses
from engine.serializers import LessonSerializer, LessonSlotSerializer
from frontend.utils import get_user_from_token, is_authenticated


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
        if 'auth_token' in self.request.COOKIES:
            user = get_user_from_token(self.request.COOKIES.get('auth_token'))
            teacher_accounts = {}
            accounts = user.teacher_profile_data.accounts.all()
            for account in accounts:
                teacher_accounts[account.account_type] = account
            context.update({
                'user': user,
                'teacher_accounts': teacher_accounts,
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
        user = self.get_user()
        context = super().get_context_data(**kwargs)
        tz_now = timezone.now().astimezone(pytz.UTC)
        lessonslots = LessonSlots.objects.filter(
            Q(lesson_from__lte=tz_now) | Q(lesson_to__lte=tz_now),
            lesson__status=LessonStatuses.ACTIVE,
            creator=user.teacher_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id').count()
        serializer = LessonSlotSerializer(lessonslots, many=True)
        context['lessons_slots'] = serializer.data
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context

    def get_user(self):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return get_user_from_token(self.request.COOKIES.get('auth_token'))
        else:
            return False


class DashboardSchedulesUpcomingSessions(TemplateView):
    """
    Dashboard Schedules Upcoming Sessions
    """
    template_name = "dashboard/schedules/upcoming.html"

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super().get_context_data(**kwargs)
        tz_now = timezone.now().astimezone(pytz.UTC)
        lessonslots = LessonSlots.objects.filter(
            Q(lesson_from__gte=tz_now) | Q(lesson_to__lte=tz_now),
            lesson__status=LessonStatuses.ACTIVE,
            creator=user.teacher_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id').count()
        serializer = LessonSlotSerializer(lessonslots, many=True)
        context['lessons_slots'] = serializer.data
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context

    def get_user(self):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return get_user_from_token(self.request.COOKIES.get('auth_token'))
        else:
            return False


class DashboardLessons(TemplateView):
    """
    Dashboard Lessons
    """
    template_name = "dashboard/lessons.html"

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super().get_context_data(**kwargs)
        lessons = LessonData.objects.filter(creator=user.teacher_profile_data).order_by('-created_at')
        serializer = LessonSerializer(lessons, many=True)
        context['lessons'] = serializer.data
        if 'auth_token' in self.request.COOKIES:
            context['user'] = get_user_from_token(self.request.COOKIES.get('auth_token'))
        return context

    def get_user(self):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return get_user_from_token(self.request.COOKIES.get('auth_token'))
        else:
            return False


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
