import urllib
import pytz
from django.db.models import Q, Sum
from django.utils import timezone
from django.conf import settings
from django.views.generic import TemplateView
from django.db.models.functions import Coalesce
from engine.models import LessonData, LessonSlots, LessonStatuses, Enrollment
from engine.serializers import LessonSerializer, LessonSlotSerializer
from users.models import TeacherPageVisits, TeacherEarnings


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
            'teacher_url': "{}://{}.{}".format(settings.SCHEME,  self.request.user.teacher_profile_data.subdomain,
                                               settings.SITE_URL),
            'zoom': {
                'ZOOM_CLIENT_ID': settings.ZOOM_CLIENT_ID,
                'ZOOM_REDIRECT_URL': urllib.parse.quote_plus(settings.ZOOM_REDIRECT_URL)
            }
        })
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
        user = self.request.user
        current_date = timezone.now()

        # page visits
        try:
            visits_data = user.teacher_profile_data.page_visits.all()
            visits_data_current_year = visits_data.filter(visit_date__year=current_date.year)
            visits_data_current_month = visits_data_current_year.filter(visit_date__month=current_date.month)
            visits_data_current_week = visits_data_current_month.filter(visit_date__week=current_date.isocalendar()[1])
        except TeacherPageVisits.DoesNotExist:
            visits_data = TeacherPageVisits.objects.none()
            visits_data_current_year = TeacherPageVisits.objects.none()
            visits_data_current_month = TeacherPageVisits.objects.none()
            visits_data_current_week = TeacherPageVisits.objects.none()

        # earnings
        try:
            earnings_data = user.teacher_profile_data.earnings.all()
            earnings_data_current_year = earnings_data.filter(added_on__year=current_date.year)
            earnings_data_current_month = earnings_data_current_year.filter(added_on__month=current_date.month)
            earnings_data_current_week = earnings_data_current_month.filter(added_on__week=current_date.isocalendar()[1])
        except TeacherEarnings.DoesNotExist:
            earnings_data = TeacherEarnings.objects.none()
            earnings_data_current_year = TeacherEarnings.objects.none()
            earnings_data_current_month = TeacherEarnings.objects.none()
            earnings_data_current_week = TeacherEarnings.objects.none()

        # lesson watch time
        try:
            pass
        except LessonData.DoesNotExist:
            pass

        # lessons created
        try:
            lessons_data = user.teacher_profile_data.lessons.all()
            lessons_data_current_year = lessons_data.filter(created_at__year=current_date.year)
            lessons_data_current_month = lessons_data_current_year.filter(created_at__month=current_date.month)
            lessons_data_current_week = lessons_data_current_month.filter(created_at__month=current_date.month)
        except LessonData.DoesNotExist:
            lessons_data = LessonData.objects.none()
            lessons_data_current_year = LessonData.objects.none()
            lessons_data_current_month = LessonData.objects.none()
            lessons_data_current_week = LessonData.objects.none()

        # students
        try:
            students_data = Enrollment.objects.filter(lesson__creator=user.teacher_profile_data)
            students_data_current_year = students_data.filter(created_at__year=current_date.year)
            students_data_current_month = students_data_current_year.filter(created_at__month=current_date.month)
            students_data_current_week = students_data_current_month.filter(
                created_at__week=current_date.isocalendar()[1])
        except Enrollment.DoesNotExist:
            students_data = Enrollment.objects.none()
            students_data_current_year = Enrollment.objects.none()
            students_data_current_month = Enrollment.objects.none()
            students_data_current_week = Enrollment.objects.none()

        context.update({
            'user': user,
            'visits': {
                'all_visits': visits_data.aggregate(total=Coalesce(Sum('visits'), 0)).get('total', 0),
                'current_year': visits_data_current_year.aggregate(total=Coalesce(Sum('visits'), 0)).get('total', 0),
                'current_month': visits_data_current_month.aggregate(total=Coalesce(Sum('visits'), 0)).get('total', 0),
                'current_week': visits_data_current_week.aggregate(total=Coalesce(Sum('visits'), 0)).get('total', 0),
            },
            'earnings': {
                'all_earnings': earnings_data.aggregate(total=Coalesce(Sum('amount'), 0.0)).get('total', 0.0),
                'current_year': earnings_data_current_year.aggregate(
                    total=Coalesce(Sum('amount'), 0.0)).get('total', 0.0),
                'current_month': earnings_data_current_month.aggregate(
                    total=Coalesce(Sum('amount'), 0.0)).get('total', 0.0),
                'current_week': earnings_data_current_week.aggregate(
                    total=Coalesce(Sum('amount'), 0.0)).get('total', 0.0),
            },
            'lesson_created': {
                'total_lessons': lessons_data.count(),
                'current_year': lessons_data_current_year.count(),
                'current_month': lessons_data_current_month.count(),
                'current_week': lessons_data_current_week.count()
            },
            'students': {
                'total_students': students_data.distinct('student').count(),
                'current_year': students_data_current_year.distinct('student').count(),
                'current_month': students_data_current_month.distinct('student').count(),
                'current_week': students_data_current_week.distinct('student').count()
            },
            'my_page': "{0}://{1}.{2}".format(settings.SCHEME, user.teacher_profile_data.subdomain, settings.SITE_URL)
        })

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
