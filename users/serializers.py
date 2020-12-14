import re
import json
import _thread

from django.db import IntegrityError
from rest_framework import serializers

from notifications.views import send_signup_email
from users.constants import RESTRICTED_SUBDOMAINS
from users.models import User, TeacherProfile, TeacherAccounts, TeacherPayments
from phonenumber_field.serializerfields import PhoneNumberField

subdomain_regex_pattern = '^([a-zA-Z0-9]+[\w\-]+[a-zA-Z0-9]+)$'


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = (
            'id',
            'password',
            'is_superuser',
            'is_staff',
            'date_joined',
            'last_login',
            'groups',
            'user_permissions',
        )
        read_only_fields = (
            'email',
            'is_superuser',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'user_subscription',
        )

class UserCreateSerializer(serializers.ModelSerializer):
    '''
    User Create Serializer used for first time user signup
    '''
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=32)
    phone_no = PhoneNumberField(required=False)

    class Meta:
        model = User
        exclude = (
            'id',
            'is_superuser',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'groups',
            'user_permissions',
        )
        read_only_fields = (
            'is_superuser',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'user_type',
        )

    def create(self, validated_data):
        try:
            user = User.objects.create_creator_user(validated_data.pop("email"), validated_data.pop("password"),
                                                    **validated_data)
            _thread.start_new_thread(send_signup_email, (user,))
            return user
        except IntegrityError as e:
            error = dict({'error': str(e)})
            raise serializers.ValidationError(error)


class TeacherAccountsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherAccounts
        fields = (
            'account_type',
            'info'
        )


class TeacherPaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherPayments
        fields = (
            'payment_type',
            'info'
        )


class TeacherProfileSerializer(serializers.ModelSerializer):
    accounts = TeacherAccountsSerializer(many=True, read_only=True)
    payments = TeacherPaymentsSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherProfile
        fields = (
            'year_of_experience',
            'subdomain',
            'description',
            'intro_video',
            'accounts',
            'payments',
        )

    def validate_subdomain(self, value):
        if value in RESTRICTED_SUBDOMAINS:
            raise serializers.ValidationError("Subdomain not permitted!")
        elif bool(re.match(subdomain_regex_pattern, value)):
            try:
                teacher = TeacherProfile.objects.exclude(user=self.request.user).get(subdomain=value)
                raise serializers.ValidationError("Subdomain not available or already in use.")
            except TeacherProfile.DoesNotExist:
                return value
        else:
            raise serializers.ValidationError("Invalid subdomain. Subdomain has to be atleast 4 character long "
                                              "and cannot start and end with _ or - and cannot contain full stop(.)")


class TeacherUserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=32)
    phone_no = PhoneNumberField(required=False)

    class Meta:
        model = User
        exclude = (
            'id',
            'is_superuser',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'groups',
            'user_permissions',
        )
        read_only_fields = (
            'is_superuser',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'user_type',
        )

    def create(self, validated_data):
        try:
            user = User.objects.create_creator_user(validated_data.pop("email"), validated_data.pop("password"),
                                                    **validated_data)
            _thread.start_new_thread(send_signup_email, (user,))
            return user
        except IntegrityError as e:
            error = dict({'error': str(e)})
            raise serializers.ValidationError(error)


class SendOTPSerializer(serializers.Serializer):
    phone_no = PhoneNumberField(required=True)


class SubdomainCheckSerializer(serializers.Serializer):
    subdomain = serializers.CharField(required=True)

    def validate_subdomain(self, value):
        if value in RESTRICTED_SUBDOMAINS:
            raise serializers.ValidationError("Subdomain not permitted!")
        elif bool(re.match(subdomain_regex_pattern, value)):
            try:
                teacher = TeacherProfile.objects.get(subdomain=value)
                raise serializers.ValidationError("Subdomain not available or already in use.")
            except TeacherProfile.DoesNotExist:
                print("Actual right case")
                return value
        else:
            raise serializers.ValidationError("Invalid subdomain. Subdomain has to be atleast 4 character long "
                                              "and cannot start and end with _ or - and cannot contain full stop(.)")


class VerifyOTPSerializer(serializers.Serializer):
    phone_no = PhoneNumberField(required=True)
    otp = serializers.CharField(max_length=6, required=True)


class TeacherPaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPayments
        fields = ['payment_type', 'info']


class TeacherProfileCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherProfile
        exclude = (
            'id',
            'user'
        )


class TeacherProfileSerializer(serializers.ModelSerializer):
    accounts = TeacherAccountsSerializer(many=True, read_only=True)
    payments = TeacherPaymentsSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherProfile
        fields = [
            'user', 'year_of_experience', 'subdomain',
            'description', 'intro_video', 'accounts',
            'payments'
        ]


class TeacherPaymentRemoveSerializer(serializers.Serializer):
    payment_type = serializers.CharField(max_length=10, required=True)


class TeacherAccountRemoveSerializer(serializers.Serializer):
    account_type = serializers.CharField(max_length=10, required=True)
