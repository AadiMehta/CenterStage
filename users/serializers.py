import json
import _thread

from notifications.views import send_signup_email
from rest_framework import serializers
from users.models import User, TeacherProfile, TeacherAccounts, TeacherPayments
from django.db import IntegrityError


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
            'is_active',
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
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=32)

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
        )

    def create(self, validated_data):
        try:
            user = User.objects.create_user(validated_data.pop("email"), validated_data.pop("password"),
                                            **validated_data)
            _thread.start_new_thread(send_signup_email, (user,))
            return user
        except IntegrityError as e:
            error = dict({'error': "User with email already present"})
            raise serializers.ValidationError(error)


class TeacherAccountsSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = TeacherAccounts
        fields = ['account_type', 'info']
    
    def get_info(self, instance):
        if instance.info:
            return json.loads(instance.info)
        return {}


class TeacherPaymentsSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPayments
        fields = ['payment_type', 'info']
    
    def get_info(self, instance):
        if instance.info:
            return json.loads(instance.info)
        return {}


class TeacherProfileCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = [
            'user', 'year_of_experience', 'subdomain',
            'about', 'intro_video'
        ]

class TeacherProfileGetSerializer(serializers.ModelSerializer):
    accounts = TeacherAccountsSerializer(many=True, read_only=True)
    payments = TeacherPaymentsSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherProfile
        fields = [
            'user', 'year_of_experience', 'subdomain',
            'about', 'intro_video', 'accounts', 'payments'
        ]

