import uuid
from django.utils import timezone
from django.db import models
from django.db.models import Q, Count, Avg
from django.conf import settings
from users.models import TeacherProfile, StudentProfile, User
from users.s3_storage import S3_LessonCoverImage_Storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from enum import Enum
from frontend.utils.auth import get_time_duration
from stream_django import activity
from users.models import User


class LessonFilterType(Enum):
    ONE_ON_ONE = "ONE_ON_ONE"
    GROUP = "GROUP"
    PERSONAL_COACHING = "PERSONAL_COACHING"
    RECENT = "RECENT"
    POPULAR = "POPULAR"
    TOP_RATED = "TOP_RATED"
    ATOZ = "ATOZ"
    ZTOA = "ZTOA"

class SessionTypes(models.TextChoices):
    SINGLE_SESSION = 'SINGLE', _('Single Session')
    MULTI_SESSION = 'MULTI', _('Multi Session')
    ONGOING_SESSION = 'ONGOING', _('Ongoing Session')


class LessonTypes(models.TextChoices):
    ONE_ON_ONE = 'ONE_ON_ONE', _('One on One Lesson Type')
    GROUP = 'GROUP', _('Group Lesson')


class NoteSubscriptionTypes(models.TextChoices):
    ONETIME = 'ONETIME', _('One Time Subscripton Type')
    MONTHLY = 'MONTHLY', _('Monthly Subscription Type')
    WEEKLY = 'WEEKLY', _('Weekly Subscription Type')
    ANNUAL = 'ANNUAL', _('Annualy Subscription Type')


class MeetingTypes(models.TextChoices):
    FREE = 'FREE', _('FREE')
    PAID = 'PAID', _('PAID')
    SCHEDULE = 'SCHEDULE', _('SCHEDULE')
    HOST_LESSON = 'HOST_LESSON', _('HOST_LESSON')


class LessonStatuses(models.TextChoices):
    ACTIVE = 'ACTIVE', _('ACTIVE')
    DELETED = 'DELETED', _('DELETED')
    REMOVED = 'REMOVED', _('REMOVED')


class EnrollmentChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', _('ACTIVE')
    STUDENT_CANCELLED = 'STUDENT_CANCELLED', _('STUDENT_CANCELLED')
    TEACHER_CANCELLED = 'TEACHER_CANCELLED', _('TEACHER_CANCELLED')


class LessonData(models.Model):
    """
    All lesson data is stored in this model
    """
    creator = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="lessons")
    name = models.CharField(_("Name of the lesson"), max_length=256)
    description = models.TextField(_("Description of the lesson"), blank=True, null=True)
    no_of_participants = models.IntegerField(_('No of participants'), default=1)
    language = models.JSONField(default=list)
    lesson_type = models.CharField(
        _("Type of lesson"), null=True, choices=LessonTypes.choices, max_length=10)
    session_type = models.CharField(
        _("Type of lesson"), choices=SessionTypes.choices, max_length=10)
    meeting_type = models.CharField(
        _("Type of Meeting"), choices=MeetingTypes.choices, max_length=20)
    price = models.JSONField(default=dict)
    timezone = models.CharField(
        _("Timezone of the lesson"), null=True, max_length=100)
    meeting_info = models.JSONField(default=dict)
    meeting_link = models.URLField(max_length=200, null=True, blank=True)
    lesson_uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    is_private = models.BooleanField(_('Lesson Privacy'), default=False)
    cover_image = models.ImageField(
        _("Lesson Cover image"), storage=S3_LessonCoverImage_Storage(), null=True)
    intro_video = models.URLField(max_length=200, null=True, blank=True)
    learnings = models.JSONField(default=list)
    requirements = models.JSONField(default=list)
    notes = models.JSONField(default=list)
    status = models.CharField(_("Lesson Status"), null=True, choices=LessonStatuses.choices, max_length=7,
                              help_text="Lesson status", default=LessonStatuses.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def permalink(self):
        "Returns permalink for lesson"
        return '{}/lesson/{}'.format(settings.BASE_URL, self.lesson_uuid)

    def seats_remaining(self):
        enrolled_count = self.enrollments.distinct('student').count()
        seats_remaining = self.no_of_participants - enrolled_count
        return seats_remaining

    def upcoming_slots(self):
        return self.slots.all().filter(Q(lesson_from__gt=timezone.now()))

    def enrollments(self):
        return self.enrollments.all()
    
    def is_student_enrolled(self, student):
        return self.enrollments.filter(student=student).exists()


class LessonSlots(models.Model):
    """
    Datetime slots of the lessons
    """
    creator = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="slots")
    lesson = models.ForeignKey(
        LessonData, on_delete=models.CASCADE, related_name="slots")
    lesson_from = models.DateTimeField(_("Start of the lesson"), null=True)
    session_no = models.IntegerField(_('Session Number'), null=True)
    lesson_to = models.DateTimeField(_("End of the lesson"))
    calendar_info = models.JSONField(default=dict, null=True)
    slot_booked = models.BooleanField(_('Slot Booked Status'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def session_duration(self):
        return get_time_duration(self.lesson_to - self.lesson_from, formatted=True)


class Meeting(models.Model):
    """
    Meeting Model
    """
    creator = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="meetings")
    topic = models.CharField(_("Topic of the meeting"), max_length=256)
    price = models.JSONField(default=dict)
    invitees = models.JSONField(default=list)
    meeting_info = models.JSONField(default=dict)
    meeting_link = models.URLField(max_length=200, null=True, blank=True)
    meeting_type = models.CharField(
        _("Type of Meeting"), choices=MeetingTypes.choices, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Enrollment(models.Model):
    """
    Enrollment Model
    """
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    lesson = models.ForeignKey(
        LessonData, on_delete=models.CASCADE, related_name="enrollments")
    lessonslot = models.ForeignKey(
        LessonSlots, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(
        _("Status of Enrollment"), choices=EnrollmentChoices.choices, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LessonRating(models.Model):
    """
    Rating Model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    lesson = models.ForeignKey(LessonData, on_delete=models.CASCADE, related_name="ratings")
    rate = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5.0)],)
    review = models.CharField(_("Review"), max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)


class LessonLikes(models.Model):
    """
    Likes Model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    lesson = models.ForeignKey(LessonData, on_delete=models.CASCADE, related_name="likes")
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="likes")
    lesson = models.ForeignKey(
        LessonData, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)


class NoteData(models.Model):
    """
    Note Model
    """
    creator = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="notes")
    name = models.CharField(_("Name of the Note"), max_length=256)
    language = models.CharField(_('Note language'), null=True, max_length=30)
    subscription_type = models.CharField(
        _("Subscription Type of Note"), null=True, choices=NoteSubscriptionTypes.choices, max_length=10)
    reading_duration = models.IntegerField(
        _('No. of Hours for Reading'), null=True)
    cover_image = models.ImageField(
        _("Note Cover image"), storage=S3_LessonCoverImage_Storage(), null=True)
    is_private = models.BooleanField(_('Note Privacy'), default=False)
    documents = models.JSONField(default=list)
    drive_url = models.URLField(max_length=200, null=True, blank=True)
    price = models.JSONField(default=list)
    learnings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Post(activity.Activity, models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_post")
    title = models.CharField(max_length=160)
    text = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User, related_name='friends', on_delete=models.CASCADE)
    target = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')
