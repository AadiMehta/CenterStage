import logging
from rest_framework import status
from rest_framework import generics
from users.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from users.serializers import UserSerializer, UserCreateSerializer, ThirdPartyAuthSerializer, \
    ThirdPartyAuthValidationSerializer, LoginResponseSerializer
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
