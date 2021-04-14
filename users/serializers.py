import re
import _thread
from django.db.models import Avg, Count
from notifications.views import send_signup_email
from rest_framework import serializers
from users.constants import RESTRICTED_SUBDOMAINS
from users.models import User, TeacherProfile, Accounts, PaymentAccounts, StudentProfile, TeacherRating
from django.db import IntegrityError
from phonenumber_field.serializerfields import PhoneNumberField

subdomain_regex_pattern = '^([a-zA-Z0-9]+[\w\-]+[a-zA-Z0-9]+)$'


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128)


class UserSerializer(serializers.ModelSerializer):

    created_at = serializers.SerializerMethodField()

    @staticmethod
    def get_created_at(instance):
        return instance.date_joined.strftime('%A, %d %b %Y')
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
            'created_at'
        )


class AccountsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Accounts
        fields = (
            'account_type',
            'info'
        )


class TeacherPaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAccounts
        fields = (
            'stripe_account_id',
            'info'
        )


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    accounts = AccountsSerializer(many=True, read_only=True)
    payments = TeacherPaymentsSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    @staticmethod
    def get_avg_rating(instance):
        ratings = TeacherRating.objects.filter(creator=instance).aggregate(Avg('rate'))
        return round(ratings.get('rate__avg') or 0, 1)

    class Meta:
        model = TeacherProfile
        fields = (
            'user',
            'profession',
            'profile_image',
            'year_of_experience',
            'subdomain',
            'bio',
            'intro_video',
            'avg_rating',
            'accounts',
            'payments',
        )

    def validate_subdomain(self, value):
        if value in RESTRICTED_SUBDOMAINS:
            raise serializers.ValidationError("Subdomain not permitted!")
        elif bool(re.match(subdomain_regex_pattern, value)):
            try:
                teacher = TeacherProfile.objects.get(subdomain=value.lower())
                raise serializers.ValidationError("Subdomain not available or already in use.")
            except TeacherProfile.DoesNotExist:
                return value
        else:
            raise serializers.ValidationError("Invalid subdomain. Subdomain has to be at least 4 character long "
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
            # _thread.start_new_thread(send_signup_email, (user, 'notifications/signup_mail.html'))
            return user
        except IntegrityError as e:
            error = dict({'error': str(e)})
            raise serializers.ValidationError(error)


class TeacherProfileCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherProfile
        exclude = (
            'id',
            'user'
        )


class SubdomainCheckSerializer(serializers.Serializer):
    subdomain = serializers.CharField(required=True)

    def validate_subdomain(self, value):
        if value in RESTRICTED_SUBDOMAINS:
            raise serializers.ValidationError("Subdomain not permitted!")
        elif bool(re.match(subdomain_regex_pattern, value)):
            try:
                teacher = TeacherProfile.objects.get(subdomain=value.lower())
                raise serializers.ValidationError("Subdomain not available or already in use.")
            except TeacherProfile.DoesNotExist:
                return value
        else:
            raise serializers.ValidationError("Invalid subdomain. Subdomain has to be atleast 4 character long "
                                              "and cannot start and end with _ or - and cannot contain full stop(.)")


class TeacherPaymentRemoveSerializer(serializers.Serializer):
    payment_type = serializers.CharField(max_length=10, required=True)


class TeacherAccountRemoveSerializer(serializers.Serializer):
    account_type = serializers.CharField(max_length=10, required=True)


# ********* Student Serializers **********
class StudentUserCreateSerializer(serializers.ModelSerializer):
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
            user = User.objects.create_student_user(validated_data.pop("email"), validated_data.pop("password"),
                                                    **validated_data)
            # _thread.start_new_thread(send_signup_email, (user,))
            return user
        except IntegrityError as e:
            error = dict({'error': str(e)})
            raise serializers.ValidationError(error)


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = (
            'profile_image',
            'bio',
            'status',
        )


# ********* Common Serializers ***********
class SendOTPSerializer(serializers.Serializer):
    phone_no = PhoneNumberField(required=True)


class VerifyOTPSerializer(serializers.Serializer):
    phone_no = PhoneNumberField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
