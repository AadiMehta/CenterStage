from django.db.models.signals import post_save, pre_save
from payments.models import LessonPayment
from .utils import unique_payment_id_generator


def pre_save_lesson_payment(sender, instance, *args, **kwargs):
    if not instance.payment_identifier:
        instance.order_id = unique_payment_id_generator(instance)
