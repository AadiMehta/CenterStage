from rest_framework import serializers
from engine.models import LessonData, LessonSlots, Meeting
from users.serializers import TeacherProfileSerializer

from frontend.utils import get_time_duration


# ********* Lessons Serializers **********
class LessonCreateSerializer(serializers.ModelSerializer):
    """
    Lesson Create Serializer
    name -> required
    """
    name = serializers.CharField(required=True)

    class Meta:
        model = LessonData
        exclude = [
            'creator'
        ]

class LessonSerializer(serializers.ModelSerializer):
    """
    Lesson Serializer
    """

    class Meta:
        model = LessonData
        exclude = [
            'creator'
        ]


class LessonSlotCreateSerializer(serializers.ModelSerializer):
    """
    Lesson Slot Serializer
    """
    class Meta:
        model = LessonSlots
        exclude = [
            'creator',
            'lesson'
        ]


class LessonSlotSerializer(serializers.ModelSerializer):
    """
    Lesson Slot Serializer
    """
    lesson = LessonSerializer(read_only=True)
    creator = TeacherProfileSerializer(read_only=True)
    lesson_from = serializers.SerializerMethodField()
    lesson_to = serializers.SerializerMethodField()
    session_time = serializers.SerializerMethodField()
    session_duration = serializers.SerializerMethodField()

    def get_lesson_from(self, instance):
        return instance.lesson_from.strftime('%A, %d %b %Y')

    def get_lesson_to(self, instance):
        return instance.lesson_to.strftime('%A, %d %b %Y')

    def get_session_time(self, instance):
        return instance.lesson_from.strftime('%I:%M %p')

    def get_session_duration(self, instance):
        return get_time_duration(instance.lesson_to - instance.lesson_from, formatted=True)

    class Meta:
        model = LessonSlots
        fields = [
            'creator',
            'lesson',
            'lesson_from',
            'lesson_to',
            'created_at',
            'session_time',
            'session_duration'
        ]

# ********* Meetings Serializers **********
class MeetingCreateSerializer(serializers.ModelSerializer):
    """
    Meeting Create Serializer
    name -> required
    """
    topic = serializers.CharField(required=True)

    class Meta:
        model = Meeting
        exclude = [
            'creator'
        ]
