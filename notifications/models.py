from django.db import models
from users.models import User
# Create your models here.
models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile_data")

class Notification(models.Model):
	NOTIFICATION_TYPES = ((1,'Lesson'),(2,'Comment'), (3,'Follow'))

	sender = models.CharField(max_length=90, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_user")
	action_url = models.CharField(max_length=90,blank=True)
	notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
	text_preview = models.CharField(max_length=90, blank=True)
	date = models.DateTimeField(auto_now_add=True)
	is_seen = models.BooleanField(default=False)