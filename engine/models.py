from django.db import models
from users.models import TeacherProfile
from users.s3_storage import S3_LessonCoverImage_Storage
from django.utils.translation import ugettext_lazy as _


class LessonTypes(models.TextChoices):
    SINGLE_SESSION = 'SINGLE', _('Single Session')
    MULTI_SESSION = 'MULTI', _('Multi Session')
    ONGOING_SESSION = 'ONGOING', _('Ongoing Session')


class CurrencyTypes(models.TextChoices):
    DOLLARS = 'DOLLARS', _('DOLLARS')
    INDIAN_RUPEES = 'INDIAN_RUPEES', _('INDIAN_RUPEES')


class LessonData(models.Model):
    """
    All lesson data is stored in this model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="lessons")
    name = models.CharField(_("Name of the lesson"), max_length=256)
    description = models.TextField(_("Description of the lesson"), blank=True, null=True)
    no_of_participants = models.IntegerField(_('No of participants'), null=True)
    language = models.CharField(_('Lesson language'), max_length=30)
    lesson_type = models.CharField(_("Type of lesson"), choices=LessonTypes.choices, max_length=10)
    price_per_session = models.IntegerField(_('Price per session'), null=True)
    price_per_session_currency = models.CharField(_("Price per session currency type"), choices=CurrencyTypes.choices, max_length=20,
                                    help_text="Type of session")
    is_private = models.BooleanField(_('Lesson Privacy'), default=False)
    cover_image = models.ImageField(_("Lesson Cover image"), storage=S3_LessonCoverImage_Storage(), null=True)
    intro_video = models.URLField(max_length=200, null=True, blank=True)
    learnings = models.JSONField(default=list)
    requirements = models.JSONField(default=list)
    notes = models.JSONField(default=list)


class LessonSlots(models.Model):
    """
    Datetime slots of the lessons
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="slots")
    lesson = models.ForeignKey(LessonData, on_delete=models.CASCADE, related_name="slots")
    lesson_from = models.DateTimeField(_("Start of the lesson")),
    lesson_to = models.DateTimeField(_("End of the lesson"))
    slot_booked = models.BooleanField(_('Slot Booked Status'), default=False)
