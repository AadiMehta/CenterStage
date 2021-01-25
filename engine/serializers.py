from rest_framework import serializers
from engine.models import LessonData, LessonSlots, Meeting


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
