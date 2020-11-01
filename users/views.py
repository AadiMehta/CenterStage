import string
import random
import logging

from rest_framework import status
from rest_framework import generics
from users.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from users.serializers import UserSerializer, UserCreateSerializer, LoginResponseSerializer
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger(__name__)


class ObtainAuthToken(APIView):
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
        return Response({'token': token.key, 'preferred_marina_address': user.preferred_marina_address})


class Register(generics.CreateAPIView):
    """
    Create a user who can create trips

    {
        "email": "bob_marley@gmail.com",
        "first_name": "Bob",
        "last_name": "Marley",
        "business_name": "Noneofyours, Lic",
        "location": "somewhere in the us",
        "phone_no": "123123123",
        "preferred_marina_address": "address"
    }
    """
    serializer_class = UserCreateSerializer
    authentication_classes = []
    permission_classes = []


class Logout(APIView):

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
        "business_name": "Noneofyours, Lic",
        "location": "somewhere in the us",
        "preferred_marina_address": "address",
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


class SendOtp(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        phone_no = data.get('phone_no')
        if not phone_no and not validate_no(phone_no):
            return Response("Invalid Phone Number", status=status.HTTP_400_BAD_REQUEST)

        user = self.get_user_by_phone(phone_no)
        if not user:
            return Response("No User Found", status=status.HTTP_400_BAD_REQUEST)

        otp = self.generate_otp()
        print(otp)
        self.send_otp(phone_no, otp)
        self.persist_otp(user.id, phone_no, otp)

        return Response(dict(msg="Otp Sent Successfully"), status=status.HTTP_200_OK)

    def send_otp(self, phone_no, otp):
        # Send OTP using twilio to phone_no
        pass

    def persist_otp(self, user_id, phone_no, otp):
        # Store UserId (Key): OTP (Value) in Cache
        pass

    def generate_otp(self):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))

    def get_user_by_phone(self, phone_no):
        # Check if User with Phone Number is Present in DB
        # Return User Object
        return User(id=1)

    def validate_no(self, phone_no):
        pattern = re.compile("[1-9][0-9]{9}")
        return pattern.match(phone_no)


class VerifyOtp(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        phone_no = data.get('phone_no')
        provided_otp = data.get('otp')
        if not provided_otp:
            return Response("Invalid Data", status=status.HTTP_400_BAD_REQUEST)
        if not phone_no and not validate_no(phone_no):
            return Response("Invalid Phone Number", status=status.HTTP_400_BAD_REQUEST)

        user = self.get_user_by_phone(phone_no)
        if not user:
            return Response("No User Found", status=status.HTTP_400_BAD_REQUEST)

        cached_otp = self.get_otp_from_cache(user.id)
        if not cached_otp:
            return Response(dict(msg="Otp Expired"), status=status.HTTP_400_BAD_REQUEST)

        if provided_otp == cached_otp:
            token = self.authenticate(user)
            return Response(dict(msg="Login Successful", token=token), status=status.HTTP_200_OK)

    def authenticate(self, user):
        return "AUTHENTICATED!@#!@#TOKEN"

    def get_otp_from_cache(self, user_id):
        # GET UserId (Key) From Cache
        return "KA9JQ1"

    def generate_otp(self):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))

    def get_user_by_phone(self, phone_no):
        # Check if User with Phone Number is Present in DB
        # Return User Object
        return User(id=1)

    def validate_no(self, phone_no):
        pattern = re.compile("[1-9][0-9]{9}")
        return pattern.match(phone_no)
