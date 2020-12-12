import re
import json
import string
import random
import logging
import urllib
from django.conf import settings
from django.core.cache import cache
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from notifications.twilio_sms_notification import twilio
from users.authentication import BearerAuthentication
from users.serializers import (
    UserSerializer, TeacherUserCreateSerializer, LoginResponseSerializer, TeacherProfileSerializer,
    SendOTPSerializer, VerifyOTPSerializer, SubdomainCheckSerializer,
    TeacherPaymentsSerializer, TeacherPaymentRemoveSerializer, TeacherAccountRemoveSerializer,
    UserCreateSerializer
)
from users.models import (
    User, TeacherProfile, TeacherProfileStatuses, TeacherPayments
)


logger = logging.getLogger(__name__)


class ObtainAuthToken(APIView):
    """
    Send username and password and return Auth Token
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    @swagger_auto_schema(request_body=AuthTokenSerializer, responses={200: LoginResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class TeacherRegister(generics.CreateAPIView):
    """
    Create a teacher user on the centerstage platform

    User Type:\n
        CR -> Creator
    """
    serializer_class = TeacherUserCreateSerializer
    authentication_classes = []
    permission_classes = []


# class StudentRegister(generics.CreateAPIView):
#     """
#     Create a user on the centerstage platform
#
#     User Types:\n
#         CR -> Creator\n
#         ST -> Student\n
#         AD -> Admin
#     """
#     serializer_class = TeacherUserCreateSerializer
#     authentication_classes = []
#     permission_classes = []


class Logout(APIView):
    """
    Logs the user out. Deletes the token
    """
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        resp = dict({
            "message": "Successfully Logout"
        })
        return Response(resp, status=status.HTTP_200_OK)


class Profile(generics.RetrieveUpdateAPIView):
    """
    Get and update profile data. This data will be
    set during User registration.

    Update profile:
    {
        "first_name": "Bob",
        "last_name": "Marley",
        "phone_no": "123123123",
        "profile_image": "/users/profile_images/1.png"
    }
    """
    serializer_class = UserSerializer

    def get_object(self):
        return User.objects.get(email=self.request.user.email)
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(Profile, self).update(request, *args, **kwargs)


class ProfileImage(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            if data["image"] is not None:
                user.profile_image = data["image"]
                user.save()
                return Response(UserSerializer(user).data)
            else:
                return Response(dict({"image": ["This field is required!"]}), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(dict({"image": ["This field is required!"]}), status=status.HTTP_400_BAD_REQUEST)


class ProfileRegister(generics.CreateAPIView):
    """
    Create a user on the centerstage platform

    User Types:\n
        VR -> Visitor\n
        CR -> Creator\n
        ST -> Student\n
        AD -> Admin
    """
    serializer_class = UserCreateSerializer
    authentication_classes = []
    permission_classes = []


class SendOtp(generics.CreateAPIView):
    """
    Send OTP to phone_no after validation

    Request body:
        {
            "phone_no": "9999999999"
        }
    Response:
        {
            "msg": "Otp Sent Successfully"
        }
    """
    serializer_class = SendOTPSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_no = serializer.validated_data.get("phone_no")
        try:
            user = self.get_user_by_phone(phone_no)
        except User.DoesNotExist:
            return Response(dict({"error": "User with phone no doesn't exist"}), status=status.HTTP_401_UNAUTHORIZED)

        otp = self.generate_otp()
        print(otp)
        self.persist_otp(phone_no, otp)
        self.send_otp(phone_no, otp)

        headers = self.get_success_headers(serializer.data)
        return Response(dict({"msg": "OTP sent successfully"}), status=status.HTTP_200_OK, headers=headers)

    @staticmethod
    def send_otp(phone_no, otp):
        # Send OTP using twilio API
        message = 'OTP for CenterStage sign in : {}'.format(otp)
        twilio.send_message(body=message, to=str(phone_no))

    @staticmethod
    def persist_otp(phone_no, otp):
        # Set OTP in Cache
        cache_key = 'OTP-{0}'.format(str(phone_no))
        cache.set(cache_key, otp, 90)

    @staticmethod
    def generate_otp():
        # Generate Random OTP of 6 digits
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def get_user_by_phone(phone_no):
        # Verify if User with phone_no exist
        return User.objects.get(phone_no=phone_no)

    @staticmethod
    def validate_no(phone_no):
        # Validate phone_no
        pattern = re.compile("[1-9][0-9]{9}")
        return pattern.match(phone_no)


class VerifyOtp(generics.CreateAPIView):
    """
    Verify OTP sent to the phone_no

    Request body:
    {
        "phone_no": "9999999999"
        "otp": "01AZM6"
    }
    Response:
    {
        "msg": "Login Successful",
        "token": "3e80a3dbae01002c37a06fa5cee04fea62e96d01"
    }
    """
    serializer_class = VerifyOTPSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_no = serializer.validated_data.get("phone_no")
        provided_otp = serializer.validated_data.get('otp')

        try:
            user = self.get_user_by_phone(phone_no)
        except User.DoesNotExist:
            return Response(dict({"error": "Invalid user"}), status=status.HTTP_401_UNAUTHORIZED)

        cached_otp = self.get_otp_from_cache(phone_no)
        if not cached_otp:
            return Response(dict({"error": "Otp Expired"}), status=status.HTTP_401_UNAUTHORIZED)

        if provided_otp == cached_otp:
            token, created = self.authenticate(user)
            return Response(dict({"token": token.key}), status=status.HTTP_200_OK)
        else:
            return Response(dict({"error": "Invalid OTP"}), status=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def authenticate(user):
        # Get or Create Token for User
        return Token.objects.get_or_create(user=user)

    @staticmethod
    def get_otp_from_cache(phone_no):
        # Get OTP from Cache
        cache_key = 'OTP-{0}'.format(str(phone_no))
        return cache.get(cache_key)

    @staticmethod
    def get_user_by_phone(phone_no):
        # Verify if User with phone_no exist
        return User.objects.get(phone_no=phone_no)

    @staticmethod
    def validate_no(phone_no):
        # Validate phone_no
        pattern = re.compile("[1-9][0-9]{9}")
        return pattern.match(phone_no)


class TeacherProfileView(APIView):
    """
    API to create the additional teacher profile
    info
    """
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def get(self, request):
        try:
            teacher = TeacherProfile.objects.get(user=request.user, status=TeacherProfileStatuses.ACTIVE)
        except TeacherProfile.DoesNotExist:
            return Response(dict({"error": "Teacher is yet to create the profile"}), status=status.HTTP_400_BAD_REQUEST)

        serializer = TeacherProfileSerializer(instance=teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            if request.user.teacher_profile_data is not None:
                return Response(dict({
                    "error": "Teacher profile already created. Hit Put request to update the profile"
                }), status=status.HTTP_400_BAD_REQUEST)
        except TeacherProfile.DoesNotExist:
            serializer = TeacherProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            teacher_profile = request.user.teacher_profile_data
            serializer = TeacherProfileSerializer(teacher_profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            return Response(dict({
                "error": "Teacher profile yet to be created. Hit Post request to create the profile."
            }), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            teacher = request.user.teacher_profile_data
        except TeacherProfile.DoesNotExist:
            return Response(dict({"error": "Teacher is yet to create the profile"}))

        teacher.status = TeacherProfileStatuses.DELETED
        teacher.save()
        return Response("", status=status.HTTP_204_NO_CONTENT)


class SubdomainAvailabilityAPIView(APIView):
    """
    API to check if the subdomain is available
    on the backend. Restricted subdomains are also
    checked.
    """
    def post(self, request):
        serializer = SubdomainCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(dict({"msg": "Available"}), status=status.HTTP_200_OK)


class TeacherPaymentsAPIView(APIView):
    """
    Create or delete the Payment data for the user
    """
    def post(self, request):
        serializer = TeacherPaymentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        serializer = TeacherPaymentRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_type = serializer.validated_data.get("payment_type")
        try:
            teacher = TeacherProfile.objects.get(user=request.user, status=TeacherProfileStatuses.ACTIVE)
        except TeacherProfile.DoesNotExist:
            return Response(dict({"error": "No Active Profile Found"}))

        try:
            payment = TeacherPayments.objects.get(teacher=teacher, payment_type=payment_type)
            payment.delete()
            return Response("", status=status.HTTP_204_NO_CONTENT)
        except TeacherPayments.DoesNotExist:
            return Response(dict({"error": "No Payment Found"}))


class TeacherProfileViewTemplate(TemplateView):
    template_name = "test_teacher_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url = self.request.META['HTTP_HOST']
        subdomain = url.split('.')[0]
        teacher = TeacherProfile.objects.get(subdomain=subdomain)
        serializer = TeacherProfileSerializer(instance=teacher)
        teacher_info = serializer.data
        teacher_accounts = {}
        accounts = teacher_info.pop('accounts')
        for account in accounts:
            teacher_accounts[account['account_type']] = account
        context.update({
            'subdomain': subdomain,
            'teacher': teacher_info,
            'teacher_accounts': teacher_accounts,
            'redirection_url': url,
            'zoom': {
                'ZOOM_CLIENT_ID': settings.ZOOM_CLIENT_ID,
                'ZOOM_DISCONNECT_URL': '{}/profile/zoom/disconnect'.format(settings.API_BASE_URL, teacher.id),
                'ZOOM_CONNECT_URL': urllib.parse.quote('{}/profile/zoom/connect'.format(
                                            settings.API_BASE_URL
                                        ))
            }
        })
        return context


class AccountConnectedTemplate(TemplateView):
    template_name = "test_account_connected_success.html"
