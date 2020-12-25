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
Including another URLconf
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
from frontend.views import (
    HomeTemplateView, OnboardStep1TemplateView, OnboardStep2TemplateView,
    OnboardStep3TemplateView, AccountConnectedTemplate
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

    # Templates
    path('account/success', AccountConnectedTemplate.as_view(), name="account-connected-success"),
    path('onboarding', OnboardStep1TemplateView.as_view(), name="onboarding-step-1"),
    path('onboarding/step2', OnboardStep2TemplateView.as_view(), name="onboarding-step-2"),
    path('onboarding/step3', OnboardStep3TemplateView.as_view(), name="onboarding-step-3"),
    path('', HomeTemplateView.as_view(), name="homepage"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
