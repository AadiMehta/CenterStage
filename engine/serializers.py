import pytz
from django.utils import timezone
from rest_framework import serializers
from engine.models import LessonData, LessonSlots, Meeting
from users.serializers import TeacherProfileSerializer, StudentProfileSerializer
from frontend.utils.auth import get_time_duration
from django.db.models import Q

from engine.models import LessonData, LessonSlots, Meeting, NoteData, Post

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
            'session_no',
            'lesson_to',
            'created_at',
            'session_time',
            'session_duration'
        ]

class LessonTeacherPageSerializer(serializers.ModelSerializer):
    """
    Lesson Teacher Page Serializer
    """
    creator = TeacherProfileSerializer(read_only=True)
    upcoming_slot = serializers.SerializerMethodField()
    no_of_slots = serializers.SerializerMethodField()
    completed_sessions_count = serializers.SerializerMethodField()

    @staticmethod
    def get_upcoming_slot(instance):
        upcoming_slots = instance.slots.filter(lesson_from__gt=timezone.now()).order_by('created_at')
        return LessonSlotSerializer(upcoming_slots.first()).data

    @staticmethod
    def get_no_of_slots(instance):
        return instance.slots.count()
    
    @staticmethod
    def get_completed_sessions_count(instance):
        tz_now = timezone.now().astimezone(pytz.UTC)
        lesson_slots = instance.slots.filter(
            lesson_to__lte=tz_now
        )
        return lesson_slots.count()
    
    class Meta:
        model = LessonData
        fields = [
            'creator',
            'name',
            'description',
            'no_of_participants',
            'language',
            'lesson_type',
            'session_type',
            'meeting_type',
            'meeting_link',
            'lesson_uuid',
            'cover_image',
            'learnings',
            'requirements',
            'status',
            'price',
            'upcoming_slot',
            'no_of_slots',
            'completed_sessions_count',
            'permalink'
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


class SlotSerializer(serializers.ModelSerializer):
    """
    Lesson Slot Serializer
    """
    lesson = LessonTeacherPageSerializer(read_only=True)
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
            'session_no',
            'lesson_to',
            'created_at',
            'session_time',
            'session_duration'
        ]



class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment Serializer
    """
    lesson = LessonTeacherPageSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    lesson_from = serializers.SerializerMethodField()
    lesson_to = serializers.SerializerMethodField()
    session_time = serializers.SerializerMethodField()
    session_duration = serializers.SerializerMethodField()
    other_enrollments = serializers.SerializerMethodField()

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


    @staticmethod
    def get_other_enrollments(instance):
        return instance.lessonslot.lesson.enrollments.all()

    class Meta:
        model = LessonSlots
        fields = [
            'lesson',
            'student',
            'lesson_from',
            'session_no',
            'lesson_to',
            'created_at',
            'session_time',
            'session_duration',
            'other_enrollments'
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)

    class Meta:
        model = Post
        exclude = [
            'user'
        ]
            

class PostSerializer(serializers.ModelSerializer):


    class Meta:
            model = Post
            exclude = [
                'creator'
            ]

class NoteCreateSerializer(serializers.ModelSerializer):
    """
    Note Create Serializer
    name -> required
    """
    name = serializers.CharField(required=True)

    class Meta:
        model = NoteData
        exclude = [
            'creator'
        ]



class NoteSerializer(serializers.ModelSerializer):
    """
    Note Serializer
    """

    class Meta:
        model = NoteData
        exclude = [
            'creator'
        ]


