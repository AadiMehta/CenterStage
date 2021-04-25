from users.models import User, TeacherProfile, StudentProfile
from django.shortcuts import get_object_or_404
from  chat.models import MessageModel
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, CharField
from django.db.models import Q


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.email', read_only=True)
    recipient = CharField(source='recipient.email')

    def create(self, validated_data):
        print('in create')
        print(validated_data['recipient']['email'])
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, email=validated_data['recipient']['email'])
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body')


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)

class MessageUserSerializer(ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = TeacherProfile
        fields = ('name','email','profile_image','bio')

class MessageStudentSerializer(ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = StudentProfile
        fields = "__all__"

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ('profile_image','bio')

class LastMessageSerializer(ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ('timestamp','body')

class MessageContactSerializer(ModelSerializer):
    profile = ProfileSerializer(source='teacher_profile_data')
    last_message  = serializers.SerializerMethodField('get_last_message')

    def get_last_message(self, obj):
        # try:
        print('in serializer')
        print(self.context)
        user = self.context['user']
        try:
            user_messages = MessageModel.objects.filter((Q(recipient=user) & Q(user=obj)) | (Q(recipient=obj) & Q(user=user))).order_by('-timestamp')[0]
            if user_messages:
                last_message_serializer = LastMessageSerializer(user_messages)
                print('done')
                return last_message_serializer.data
            else:
                return ""
        except:
            return ''
        # except:
        #     return ""

    class Meta:
        model = User
        fields = ('first_name','last_name','email','profile','last_message')