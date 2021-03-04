from rest_framework import serializers
from engine.models import LessonData, LessonSlots, Meeting
from users.serializers import TeacherProfileSerializer, StudentProfileSerializer
from frontend.utils.auth import get_time_duration


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

    @staticmethod
    def get_lesson_from(instance):
        return instance.lesson_from.strftime('%A, %d %b %Y')

    @staticmethod
    def get_lesson_to(instance):
        return instance.lesson_to.strftime('%A, %d %b %Y')

    @staticmethod
    def get_session_time(instance):
        return instance.lesson_from.strftime('%I:%M %p')

    @staticmethod
    def get_session_duration(instance):
        return get_time_duration(instance.lesson_to - instance.lesson_from, formatted=True)

    class Meta:
        model = LessonSlots
        fields = [
            'creator',
            'lesson',
            'lesson_from',
            'lesson_no',
            'lesson_to',
            'created_at',
            'session_time',
            'session_duration'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment Serializer
    """
    lesson = LessonSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    lesson_from = serializers.SerializerMethodField()
    lesson_to = serializers.SerializerMethodField()
    session_time = serializers.SerializerMethodField()
    session_duration = serializers.SerializerMethodField()

    @staticmethod
    def get_lesson_from(instance):
        return instance.lessonslot.lesson_from.strftime('%A, %d %b %Y')

    @staticmethod
    def get_lesson_to(instance):
        return instance.lessonslot.lesson_to.strftime('%A, %d %b %Y')

    @staticmethod
    def get_session_time(instance):
        return instance.lessonslot.lesson_from.strftime('%I:%M %p')

    @staticmethod
    def get_session_duration(instance):
        return get_time_duration(instance.lessonslot.lesson_to - instance.lessonslot.lesson_from, formatted=True)

    class Meta:
        model = LessonSlots
        fields = [
            'creator',
            'lesson',
            'lesson_from',
            'lesson_no',
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
