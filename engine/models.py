import uuid
from django.db import models
from users.models import TeacherProfile
from users.s3_storage import S3_LessonCoverImage_Storage
from django.utils.translation import ugettext_lazy as _


class SessionTypes(models.TextChoices):
    SINGLE_SESSION = 'SINGLE', _('Single Session')
    MULTI_SESSION = 'MULTI', _('Multi Session')
    ONGOING_SESSION = 'ONGOING', _('Ongoing Session')


class LessonTypes(models.TextChoices):
    ONE_ON_ONE = 'ONE_ON_ONE', _('One on One Lession Type')
    GROUP = 'GROUP', _('Group Lession')


class MeetingTypes(models.TextChoices):
    FREE = 'FREE', _('FREE')
    PAID = 'PAID', _('PAID')
    SCHEDULE = 'SCHEDULE', _('SCHEDULE')
    HOST_LESSON = 'HOST_LESSON', _('HOST_LESSON')


class LessonData(models.Model):
    """
    All lesson data is stored in this model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="lessons")
    name = models.CharField(_("Name of the lesson"), max_length=256)
    description = models.TextField(_("Description of the lesson"), blank=True, null=True)
    no_of_participants = models.IntegerField(_('No of participants'), null=True)
    no_of_sessions = models.IntegerField(_('No of sessions'), null=True)
    language = models.CharField(_('Lesson language'), null=True, max_length=30)
    lesson_type = models.CharField(_("Type of lesson"), null=True, choices=LessonTypes.choices, max_length=10)
    session_type = models.CharField(_("Type of lesson"), choices=SessionTypes.choices, max_length=10)
    meeting_type = models.CharField(_("Type of Meeting"), choices=MeetingTypes.choices, max_length=20)
    price = models.JSONField(default=list)
    timezone = models.CharField(_("Timezone of the lesson"), null=True, max_length=100)
    meeting_link = models.URLField(max_length=200, null=True, blank=True) 
    meeting_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_private = models.BooleanField(_('Lesson Privacy'), default=False)
    cover_image = models.ImageField(_("Lesson Cover image"), storage=S3_LessonCoverImage_Storage(), null=True)
    intro_video = models.URLField(max_length=200, null=True, blank=True)
    learnings = models.JSONField(default=list)
    requirements = models.JSONField(default=list)
    notes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LessonSlots(models.Model):
    """
    Datetime slots of the lessons
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="slots")
    lesson = models.ForeignKey(LessonData, on_delete=models.CASCADE, related_name="slots")
    lesson_from = models.DateTimeField(_("Start of the lesson"))
    lesson_to = models.DateTimeField(_("End of the lesson"))
    slot_booked = models.BooleanField(_('Slot Booked Status'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Meeting(models.Model):
    """
    Meeting Model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="meetings")
    topic = models.CharField(_("Topic of the meeting"), max_length=256)
    price = models.JSONField(default=dict)
    invitees = models.JSONField(default=list)
    meeting_type = models.CharField(_("Type of Meeting"), choices=MeetingTypes.choices, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
