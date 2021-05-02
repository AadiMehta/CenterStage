import pytz
from django.utils import timezone
from django.db.models import Q, Count, Avg, F, Sum
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
    slot_available = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%A, %d %b %Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%A, %d %b %Y', read_only=True)

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

    def get_slot_available(self, instance):
        upcoming_slot = instance.slots.filter(lesson_from__gt=timezone.now()).exists()
        return upcoming_slot

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
            'permalink',
            'slot_available',
            'created_at',
            'updated_at'
        ]


class LessonDashboardSerializer(serializers.ModelSerializer):
    """
    Lesson Teacher Dashboard Serializer
    """
    creator = TeacherProfileSerializer(read_only=True)
    upcoming_slot = serializers.SerializerMethodField()
    no_of_slots = serializers.SerializerMethodField()
    completed_sessions_count = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField(read_only=True)
    rating_count = serializers.SerializerMethodField(read_only=True)
    total_hours = serializers.SerializerMethodField(read_only=True)
    total_earn_count = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format='%A, %d %b %Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%A, %d %b %Y', read_only=True)

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

    def get_total_earn_count(self, obj):
        # TODO: calculate total lesson earning
        # try:
        #     price = obj.price.get('value', 0)
        #     enrollment_count = obj.enrollments.distinct('student').count()
        #     earn_count = enrollment_count * int(price)
        #     return earn_count * 0.9
        # except Exception as e:
        #     return 'NA'
        return 'NA'

    def get_enrollment_count(self, obj):
        return obj.enrollments.distinct('student').count()

    def get_rating_count(self, obj):
        ratings = obj.ratings.aggregate(Avg('rate'))
        rating = ratings.get('rate__avg')
        return rating if rating else 'NA' 

    def get_total_hours(self, obj):
        slots = obj.slots.all().aggregate(duration=Sum(F('lesson_to') - F('lesson_from')))
        duration = slots.get('duration')
        total_hrs = 0
        if duration:
            total_hrs = int(duration.total_seconds() // 3600)
        return total_hrs

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
            'intro_video',
            'cover_image',
            'lesson_uuid',
            'cover_image',
            'learnings',
            'requirements',
            'status',
            'price',
            'upcoming_slot',
            'no_of_slots',
            'completed_sessions_count',
            'enrollment_count',
            'total_earn_count',
            'rating_count',
            'total_hours',
            'permalink',
            'created_at',
            'updated_at'
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
    lessonslot = SlotSerializer(read_only=True)
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
            'other_enrollments',
            'lessonslot'
        ]

# Student Dashboard Serializers
class LessonStudentSerializer(serializers.ModelSerializer):
    """
    Lesson Student Dashboard Serializer
    """
    creator = TeacherProfileSerializer(read_only=True)
    upcoming_slot = serializers.SerializerMethodField()
    no_of_slots = serializers.SerializerMethodField()
    completed_sessions_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%A, %d %b %Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%A, %d %b %Y', read_only=True)

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
            'intro_video',
            'cover_image',
            'lesson_uuid',
            'cover_image',
            'learnings',
            'requirements',
            'status',
            'price',
            'upcoming_slot',
            'no_of_slots',
            'completed_sessions_count',
            'permalink',
            'created_at',
            'updated_at'
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


