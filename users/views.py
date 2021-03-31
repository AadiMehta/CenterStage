import re
import base64
import string
import random
import logging
from django.core.cache import cache
from django.core.files.base import ContentFile
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
from django.utils import timezone
from users.serializers import (
    UserSerializer, TeacherUserCreateSerializer, LoginResponseSerializer, TeacherProfileSerializer,
    SendOTPSerializer, VerifyOTPSerializer, SubdomainCheckSerializer, StudentUserCreateSerializer,
    StudentProfileSerializer
)
from django.contrib.auth import login
from users.models import User, TeacherProfile, ProfileStatuses, StudentProfile
from django.conf import settings
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
        user.last_login = timezone.now()
        user.save()
        user.last_login_ip = request.headers.get("X-forwarded-for", "127.0.0.1")
        token, created = Token.objects.get_or_create(user=user)

        # clear existing sessions if any.
        # this happens if there are multiple login calls
        if "sessionid" in request.COOKIES or "auth_token" in request.COOKIES:
            try:
                # delete the auth_token
                request.user.auth_token.delete()
            except Exception as e:
                pass

            try:
                # delete the sessionid
                request.session.flush()
            except Exception as e:
                pass

        headers = dict({
            "Set-Cookie": "auth_token={}; domain={}; Path=/".format(str(token.key), str(settings.SITE_URL))
        })
        login(request, user)
        return Response({'token': token.key}, headers=headers)


class TeacherRegister(generics.CreateAPIView):
    """
    Create a teacher user (CR) on the centerstage platform

    User Types:\n
        CR -> Creator\n
        ST -> Student\n
        AD -> Admin
    """
    serializer_class = TeacherUserCreateSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        headers = dict({
            "Set-Cookie": "auth_token={}; Path=/".format(str(token.key))
        })
        login(request, user)
        return Response(dict({'token': token.key}), headers=headers, status=status.HTTP_201_CREATED)


class StudentRegister(generics.CreateAPIView):
    """
    Create a student user (ST) on the centerstage platform

    User Types:\n
        CR -> Creator\n
        ST -> Student\n
        AD -> Admin
    """
    serializer_class = StudentUserCreateSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        headers = dict({
            "Set-Cookie": "auth_token={}; Path=/".format(str(token.key))
        })
        login(request, user)
        return Response(dict({'token': token.key}), headers=headers, status=status.HTTP_201_CREATED)


class Logout(APIView):
    """
    Logs the user out. Deletes the token
    """
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        request.session.flush()
        resp = dict({
            "message": "Successfully Logout"
        })
        resp = Response(resp, status=status.HTTP_200_OK)
        resp.delete_cookie('auth_token')
        return resp


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
            logger.exception(e)
            return Response(dict({"image": ["This field is required!"]}), status=status.HTTP_400_BAD_REQUEST)


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
        "token": "<token>"
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
            logger.error("Invalid User. Phone no not registered!")
            return Response(dict({"error": "Invalid user"}), status=status.HTTP_401_UNAUTHORIZED)

        cached_otp = self.get_otp_from_cache(phone_no)
        if not cached_otp:
            return Response(dict({"error": "Otp Expired"}), status=status.HTTP_401_UNAUTHORIZED)

        if provided_otp == cached_otp:
            token, created = self.authenticate(user)
            login(request, user)
            return Response(dict({"token": token.key}), status=status.HTTP_200_OK)
        else:
            logger.error("Invalid OTP!")
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
    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    def get(self, request):
        try:
            teacher = TeacherProfile.objects.get(user=request.user, status=ProfileStatuses.ACTIVE)
        except TeacherProfile.DoesNotExist:
            logger.error("Teacher profile not created yet!")
            return Response(dict({"error": "Teacher is yet to create the profile"}), status=status.HTTP_400_BAD_REQUEST)

        serializer = TeacherProfileSerializer(instance=teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            teacher = TeacherProfile.objects.get(user=request.user)
            return Response(dict({
                "error": "Teacher profile already created. Hit Put request to update the profile"
            }), status=status.HTTP_400_BAD_REQUEST)
        except TeacherProfile.DoesNotExist:
            profile_photo = None
            if "profile_image" in request.data.keys():
                profile_photo, ext = self.base64_file(request.data.pop("profile_image"))
            serializer = TeacherProfileSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            teacher_profile = serializer.save(user=request.user)
            if profile_photo is not None:
                teacher_profile.profile_image.save(str(teacher_profile.user.first_name) + "_profile_photo." + ext,
                                                   profile_photo, save=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            teacher_profile = request.user.teacher_profile_data
            if "profile_image" in request.data.keys():
                profile_photo, ext = self.base64_file(request.data.pop("profile_image"))
                teacher_profile.profile_image.save(str(teacher_profile.user.first_name) + "_profile_photo."
                                                   + ext, profile_photo, save=True)
            serializer = TeacherProfileSerializer(teacher_profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            logger.error("Teacher profile not created yet!")
            return Response(dict({
                "error": "Teacher profile yet to be created. Hit Post request to create the profile."
            }), status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            teacher_profile = request.user.teacher_profile_data
            serializer = TeacherProfileSerializer(teacher_profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            logger.error("Teacher profile not created yet!")
            return Response(dict({
                "error": "Teacher profile not updated."
            }), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            teacher = request.user.teacher_profile_data
        except TeacherProfile.DoesNotExist:
            logger.error("Teacher profile not created yet!")
            return Response("", status=status.HTTP_204_NO_CONTENT)

        teacher.status = ProfileStatuses.DELETED
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


# class TeacherPaymentsAPIView(APIView):
#     """
#     Create or delete the Payment data for the user
#     """
#     def post(self, request):
#         serializer = TeacherPaymentsSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         serializer.save(user=request.user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def delete(self, request):
#         serializer = TeacherPaymentRemoveSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         payment_type = serializer.validated_data.get("payment_type")
#         try:
#             teacher = TeacherProfile.objects.get(user=request.user, status=ProfileStatuses.ACTIVE)
#         except TeacherProfile.DoesNotExist:
#             return Response(dict({"error": "No Active Profile Found"}))
#
#         try:
#             payment = TeacherPayments.objects.get(teacher=teacher, payment_type=payment_type)
#             payment.delete()
#             return Response("", status=status.HTTP_204_NO_CONTENT)
#         except TeacherPayments.DoesNotExist:
#             return Response(dict({"error": "No Payment Found"}))


# ************************* Student APIs *******************************

class StudentProfileView(APIView):
    """
    API to create the additional teacher profile
    info
    """
    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    def get(self, request):
        try:
            student = StudentProfile.objects.get(user=request.user, status=ProfileStatuses.ACTIVE)
        except StudentProfile.DoesNotExist:
            logger.error("Student profile not created yet!")
            return Response(dict({"error": "Student is yet to create the profile"}), status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentProfileSerializer(instance=student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        redirect_url = request.GET.get('rurl')
        try:
            student = StudentProfile.objects.get(user=request.user)
            return Response(dict({
                "error": "Teacher profile already created. Hit Put request to update the profile"
            }), status=status.HTTP_400_BAD_REQUEST)
        except StudentProfile.DoesNotExist:
            profile_photo = None
            if "profile_image" in request.data.keys():
                profile_photo, ext = self.base64_file(request.data.pop("profile_image"))
            serializer = StudentProfileSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            student_profile = serializer.save(user=request.user)
            if profile_photo is not None:
                student_profile.profile_image.save(str(student_profile.user.first_name) + "_profile_photo." + ext,
                                                   profile_photo, save=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            student_profile = request.user.student_profile_data
            if "profile_image" in request.data.keys():
                profile_photo, ext = self.base64_file(request.data.pop("profile_image"))
                student_profile.profile_image.save(str(student_profile.user.first_name) + "_profile_photo."
                                                   + ext, profile_photo, save=True)
            serializer = StudentProfileSerializer(student_profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            logger.error("Student profile not created yet!")
            return Response(dict({
                "error": "Student profile yet to be created. Hit Post request to create the profile."
            }), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            student = request.user.student_profile_data
        except StudentProfile.DoesNotExist:
            logger.error("Student profile not created yet!")
            return Response("", status=status.HTTP_204_NO_CONTENT)

        student.status = ProfileStatuses.DELETED
        student.save()
        return Response("", status=status.HTTP_204_NO_CONTENT)
