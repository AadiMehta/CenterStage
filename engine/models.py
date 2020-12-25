from django.db import models
from users.models import TeacherProfile
from django.utils.translation import ugettext_lazy as _


class LessonTypes(models.TextChoices):
    SINGLE_SESSION = 'SINGLE', _('Single Session')
    MULTI_SESSION = 'MULTI', _('Multi Session')
    ONGOING_SESSION = 'ONGOING', _('Ongoing Session')


class LessonData(models.Model):
    """
    All lesson data is stored in this model
    """
    name = models.CharField(_("Name of the lesson"), max_length=256)
    description = models.TextField(_("Description of the lesson"), blank=True, null=True)
    lesson_type = models.CharField(_("Type of lesson"), choices=LessonTypes.choices, max_length=10)
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="lessons")


class LessonSchedule(models.Model):
    """
    Datetime slots of the lessons
    """
    lesson_from = models.DateTimeField(_("Start of the lesson")),
    lesson_to = models.DateTimeField(_("End of the lesson"))
    lesson = models.ForeignKey(LessonData, on_delete=models.CASCADE, related_name="lesson_schedule")
