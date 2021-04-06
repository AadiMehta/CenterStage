"""CenterStage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from notifications.views import health_check
from users.views import (
    ObtainAuthToken, Logout, Profile, SendOtp, VerifyOtp, TeacherProfileView, SubdomainAvailabilityAPIView,
    TeacherRegister, StudentRegister, StudentProfileView
)
from zoom.views import ZoomConnectAPIView, ZoomDisconnectAPIView, ZoomMeetingAPIView
from frontend.views.main import (
    HomeTemplateView, TermsAndConditionsView, PrivacyPolicyView, Faqs, ZoomPolicyView
)
from frontend.views.calendar import (
    AuthorizeGoogleCalendar, GoogleCalendarCallback, GoogleDisconnectAPIView
)
from frontend.views.onboarding import (
    StudentOnboardStep1TemplateView, OnboardStep1TemplateView, OnboardStep2TemplateView,
    OnboardStep3TemplateView, AccountConnectedTemplate
)
from frontend.views.lesson import LessonCreateWizard, AcceptFileAPI, LikeLessonAPIView
from frontend.views.schedule import ScheduleCreateWizard
from frontend.views.booking import BookLessonWizard

from frontend.views.dashboard import (
    DashboardAccountAlerts, DashboardAccountInfo, DashboardAccountPayment,
    DashboardLessons, DashboardMessages, DashboardSchedulesPastSessions,
    DashboardSchedulesUpcomingSessions, DashboardStatistics, DashboardStudents
)

from frontend.views.studentdashboard import (
    StudentDashboardEnrollments, StudentDashboardAccountAlerts, StudentDashboardAccountInfo, StudentDashboardMessages, 
    StudentDashboardSchedulesPastSessions, StudentDashboardSchedulesUpcomingSessions
)
from engine.views import LessonAPIView, MeetingAPIView
from frontend.views.public import (
    TeacherPageView, SubmitTeacherReview, RecommendTeacherAPIView,
    FollowTeacherAPIView, LikeTeacherAPIView
)


schema_view = get_schema_view(
   openapi.Info(
      title="CenterStage APIs",
      default_version='v1',
      description="Swagger document to try out all APIs for the CenterStage backend",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="tanay@centerstage.live"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

admin.site.site_header = 'CenterStage Administration'           # default: "Django Administration"
admin.site.index_title = 'CenterStage Admin Area'               # default: "Site administration"
admin.site.site_title = 'CenterStage Admin'

urlpatterns = [
    # path('admin/', admin.site.urls, name="admin"),

    path('health/check/', health_check, name="health_check"),

    # redoc and swagger documents
    url(r'swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # login APIs
    path('api/login/', ObtainAuthToken.as_view()),
    path('api/logout/', Logout.as_view()),
    path('api/profile/', Profile.as_view()),
    path('api/otp/send/', SendOtp.as_view()),
    path('api/otp/verify/', VerifyOtp.as_view()),

    # Teacher APIs
    path('api/teacher/register/', TeacherRegister.as_view()),
    path('api/teacher/profile/', TeacherProfileView.as_view()),
    path('api/teacher/subdomain/availability/', SubdomainAvailabilityAPIView.as_view()),
    # path('api/profile/teacher/accounts/', AccountsAPIView.as_view()),
    # path('api/profile/teacher/payments/', TeacherPaymentsAPIView.as_view()),
    path('api/teacher/zoom/meeting/', ZoomMeetingAPIView.as_view()),

    # Student APIs
    path('api/student/register/', StudentRegister.as_view()),
    path('api/student/profile/', StudentProfileView.as_view()),

    # zoom APIs
    path('api/profile/zoom/connect', ZoomConnectAPIView.as_view(), name="zoom-connect"),
    path('api/profile/zoom/disconnect', ZoomDisconnectAPIView.as_view(), name="zoom-disconnect"),

    # Google APIs
    path('api/profile/google/calendar/connect', AuthorizeGoogleCalendar.as_view(), name="calendar-oauth-initiate"),
    path('api/profile/google/calendar/oauth/callback', GoogleCalendarCallback.as_view(), name="calendar-oauthcallback"),
    path('api/profile/google/calendar/disconnect', GoogleDisconnectAPIView.as_view(), name="calendar-disconnect"),

    # Lesson APIs
    path('api/lesson/', LessonAPIView.as_view()),
    path('api/lesson/upload/', AcceptFileAPI.as_view()),
    path('api/teacher/like/', LikeLessonAPIView.as_view()),

    # Meeting APIs
    path('api/meeting/', MeetingAPIView.as_view()),

    # Teacher Page API
    path('api/teacher/review/', SubmitTeacherReview.as_view()),
    path('api/teacher/recommend/', RecommendTeacherAPIView.as_view()),
    path('api/teacher/follow/', FollowTeacherAPIView.as_view()),
    path('api/teacher/like/', LikeTeacherAPIView.as_view()),

    # Onboarding Templates
    path('account/success', AccountConnectedTemplate.as_view(), name="account-connected-success"),
    
    path('student/onboarding', StudentOnboardStep1TemplateView.as_view(), name="student-onboarding-step-1"),
    
    path('teacher/onboarding', OnboardStep1TemplateView.as_view(), name="onboarding-step-1"),
    path('teacher/onboarding/accounts', OnboardStep2TemplateView.as_view(), name="onboarding-step-2"),
    path('teacher/onboarding/intro-video', OnboardStep3TemplateView.as_view(), name="onboarding-step-3"),

    # Lesson Wizard
    path('lesson/new', LessonCreateWizard.as_view(LessonCreateWizard.FORMS), name="new-lesson"),
    path('schedule/new', ScheduleCreateWizard.as_view(ScheduleCreateWizard.FORMS), name="new-schedule"),

    # Book Lesson Wizard
    path('lesson/<uuid:lesson_uuid>/book', BookLessonWizard.as_view(BookLessonWizard.FORMS), name="book-lesson"),


    # Dashboard Templates
    path('student/dashboard', StudentDashboardEnrollments.as_view(), name="student-dashboard-main"),
    path('student/dashboard/enrollments', StudentDashboardEnrollments.as_view(), name="student-dashboard-enrollments"),
    path('student/dashboard/account/alerts', StudentDashboardAccountAlerts.as_view(),
         name="student-dashboard-account-alerts"),
    path('student/dashboard/account/info', StudentDashboardAccountInfo.as_view(),
         name="student-dashboard-account-info"),
    path('student/dashboard/schedules/pastsessions', StudentDashboardSchedulesPastSessions.as_view(),
         name="student-dashboard-schedules-past-sessions"),
    path('student/dashboard/schedules/upcoming', StudentDashboardSchedulesUpcomingSessions.as_view(),
         name="student-dashboard-schedules-upcoming-sessions"),
    path('student/dashboard/messages', StudentDashboardMessages.as_view(), name="student-dashboard-messages"),


    # Dashboard Templates
    path('dashboard', DashboardLessons.as_view(), name="dashboard-main"),
    path('dashboard/lessons', DashboardLessons.as_view(), name="dashboard-lessons"),
    path('dashboard/account/alerts', DashboardAccountAlerts.as_view(), name="dashboard-account-alerts"),
    path('dashboard/account/info', DashboardAccountInfo.as_view(), name="dashboard-account-info"),
    path('dashboard/account/payment', DashboardAccountPayment.as_view(), name="dashboard-account-payment"),
    path('dashboard/schedules/pastsessions', DashboardSchedulesPastSessions.as_view(),
         name="dashboard-schedules-past-sessions"),
    path('dashboard/schedules/upcoming', DashboardSchedulesUpcomingSessions.as_view(),
         name="dashboard-schedules-upcoming-sessions"),
    path('dashboard/messages', DashboardMessages.as_view(), name="dashboard-messages"),
    path('dashboard/statistics', DashboardStatistics.as_view(), name="dashboard-statistics"),
    path('dashboard/my-students', DashboardStudents.as_view(), name="dashboard-students"),

    path('centrestage/teacherpagetest', TeacherPageView.as_view(), name="teacher-page"),

    # Home Page Template
    path('', HomeTemplateView.as_view(), name="homepage"),
    path('centrestage/terms-and-conditions', TermsAndConditionsView.as_view(), name="terms-and-conditions"),
    path('centrestage/privacy-policy', PrivacyPolicyView.as_view(), name="privacy-policy"),
    path('centrestage/zoom-policy', ZoomPolicyView.as_view(), name="privacy-policy"),
    path('centrestage/faqs', Faqs.as_view(), name="faqs"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
