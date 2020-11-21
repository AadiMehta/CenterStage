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
from users.views import (
    SendOtp, VerifyOtp, TeacherProfileAPIView, TeacherProfileView,
    SubdomainAvailibilityAPIView, TeacherPaymentsAPIView,
    TeacherAccountsAPIView, TeacherRegister, ObtainAuthToken, Logout
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

    # redoc and swagger documents
    url(r'swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # login APIs
    path('api/teacher/register/', TeacherRegister.as_view()),
    path('api/login/', ObtainAuthToken.as_view()),
    path('api/logout/', Logout.as_view()),
    path('api/verify_otp/', VerifyOtp.as_view()),
    path('api/send_otp/', SendOtp.as_view()),

    path('api/profile/subdomain/validate/', SubdomainAvailibilityAPIView.as_view()),
    path('api/profile/teacher/<int:id>/', TeacherProfileAPIView.as_view()),
    path('api/profile/teacher/accounts/', TeacherAccountsAPIView.as_view()),
    path('api/profile/teacher/payments/', TeacherPaymentsAPIView.as_view()),
    path('api/profile/teacher/', TeacherProfileAPIView.as_view()),

    path('', TeacherProfileView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
