import urllib
import pytz
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.views.generic import TemplateView
from engine.models import LessonStatuses, Enrollment
from engine.serializers import EnrollmentSerializer


class StudentDashboardEnrollments(TemplateView):
    """
    Dashboard Enrollments
    """
    template_name = "student/dashboard/enrollments.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        enrollments = Enrollment.objects.filter(
            student=user.student_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id')
        serializer = EnrollmentSerializer(enrollments, many=True)
        context['enrollments'] = serializer.data
        context['user'] = user
        return context


class StudentDashboardAccountAlerts(TemplateView):
    """
    Dashboard Account Alerts
    """
    template_name = "student/dashboard/account/alerts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class StudentDashboardAccountInfo(TemplateView):
    """
    Dashboard Account Info
    """
    template_name = "student/dashboard/account/info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        user = self.request.user
        student_accounts = {}
        context.update({
            'user': user,
            'student_accounts': student_accounts,
            'BASE_URL': settings.BASE_URL,
            'zoom': {
                'ZOOM_CLIENT_ID': settings.ZOOM_CLIENT_ID,
                'ZOOM_REDIRECT_URL': urllib.parse.quote_plus(settings.ZOOM_REDIRECT_URL)
            }
        })
        context['site_name'] = settings.SITE_URL
        return context


class StudentDashboardSchedulesPastSessions(TemplateView):
    """
    Dashboard Schedules Past Sessions
    """
    template_name = "student/dashboard/schedules/pastsessions.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        tz_now = timezone.now().astimezone(pytz.UTC)
        enrollments = Enrollment.objects.filter(
            Q(lessonslot__lesson_from__lte=tz_now) | Q(lessonslot__lesson_to__lte=tz_now),
            lesson__status=LessonStatuses.ACTIVE,
            student=user.student_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id')
        serializer = EnrollmentSerializer(enrollments, many=True)
        context['enrollments'] = serializer.data
        context['user'] = self.request.user
        return context


class StudentDashboardSchedulesUpcomingSessions(TemplateView):
    """
    Dashboard Schedules Upcoming Sessions
    """
    template_name = "student/dashboard/schedules/upcoming.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        tz_now = timezone.now().astimezone(pytz.UTC)
        enrollments = Enrollment.objects.filter(
            Q(lessonslot__lesson_from__gte=tz_now) | Q(lessonslot__lesson_to__lte=tz_now),
            lesson__status=LessonStatuses.ACTIVE,
            student=user.student_profile_data
        ).order_by('-created_at').order_by('lesson_id').distinct('lesson_id')
        serializer = EnrollmentSerializer(enrollments, many=True)
        context['enrollments'] = serializer.data
        context['user'] = self.request.user
        return context


class StudentDashboardMessages(TemplateView):
    """
    Dashboard Messages
    """
    template_name = "student/dashboard/messages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
