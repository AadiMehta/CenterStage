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
    TeacherRegister, StudentRegister
)
from zoom.views import ZoomConnectAPIView, ZoomDisconnectAPIView, ZoomMeetingAPIView
from frontend.views.main import (
    HomeTemplateView, TermsAndConditionsView
)
from frontend.views.onboarding import (
    OnboardStep1TemplateView, OnboardStep2TemplateView, OnboardStep3TemplateView,
    AccountConnectedTemplate
)
from frontend.views.lesson import (
    LessonCreateStep1TemplateView, LessonCreateStep2TemplateView, LessonCreateStep3TemplateView,
    LessonCreateStep4TemplateView, LessonCreatePreviewTemplateView, LessonCreateWizard
)
from frontend.views.dashboard import (
    DashboardAccountAlerts, DashboardAccountInfo, DashboardAccountPayment,
    DashboardLessons, DashboardMessages, DashboardSchedulesPastSessions,
    DashboardSchedulesUpcomingSessions, DashboardStatistics
)
from engine.views import LessonAPIView


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
    path('admin/', admin.site.urls),

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
    # path('api/profile/teacher/accounts/', TeacherAccountsAPIView.as_view()),
    # path('api/profile/teacher/payments/', TeacherPaymentsAPIView.as_view()),
    path('api/teacher/zoom/meeting/', ZoomMeetingAPIView.as_view()),

    # Student APIs
    path('api/student/register/', StudentRegister.as_view()),

    # zoom APIs
    path('api/profile/zoom/connect', ZoomConnectAPIView.as_view()),
    path('api/profile/zoom/disconnect', ZoomDisconnectAPIView.as_view()),

    # Lesson APIs
    path('api/lesson/', LessonAPIView.as_view()),

    # Onboarding Templates
    path('account/success', AccountConnectedTemplate.as_view(), name="account-connected-success"),
    path('onboarding', OnboardStep1TemplateView.as_view(), name="onboarding-step-1"),
    path('onboarding/accounts', OnboardStep2TemplateView.as_view(), name="onboarding-step-2"),
    path('onboarding/intro-video', OnboardStep3TemplateView.as_view(), name="onboarding-step-3"),

    # Lesson Creation Templates
    path('lesson/create', LessonCreateStep1TemplateView.as_view(), name="lesson-creation-step-1"),
    path('lesson/schedule', LessonCreateStep2TemplateView.as_view(), name="lesson-creation-step-2"),
    path('lesson/intro', LessonCreateStep3TemplateView.as_view(), name="lesson-creation-step-3"),
    path('lesson/notes', LessonCreateStep4TemplateView.as_view(), name="lesson-creation-step-4"),
    path('lesson/preview', LessonCreatePreviewTemplateView.as_view(), name="lesson-creation-preview"),

    # Lesson Wizard
    path('lesson/', LessonCreateWizard.as_view(LessonCreateWizard.FORMS)),

    # Dashboard Templates
    path('dashboard/account/alerts', DashboardAccountAlerts.as_view(), name="dashboard-account-alerts"),
    path('dashboard/account/info', DashboardAccountInfo.as_view(), name="dashboard-account-info"),
    path('dashboard/account/payment', DashboardAccountPayment.as_view(), name="dashboard-account-payment"),
    path('dashboard/schedules/pastsessions', DashboardSchedulesPastSessions.as_view(),
         name="dashboard-schedules-past-sessions"),
    path('dashboard/schedules/upcoming', DashboardSchedulesUpcomingSessions.as_view(),
         name="dashboard-schedules-upcoming-sessions"),
    path('dashboard/lessons', DashboardLessons.as_view(), name="dashboard-lessons"),
    path('dashboard/messages', DashboardMessages.as_view(), name="dashboard-messages"),
    path('dashboard/statistics', DashboardStatistics.as_view(), name="dashboard-statistics"),
 
    # Home Page Template
    path('', HomeTemplateView.as_view(), name="homepage"),
    path('terms-and-conditions', TermsAndConditionsView.as_view(), name="terms-and-conditions"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
