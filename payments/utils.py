
import datetime
import os
import random
import string

from django.utils import timezone
from django.utils.text import slugify


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_payment_id_generator(instance):
    """
    This is for an payment_identifier field
    """
    payment_new_id = random_string_generator()

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(
        payment_identifier=payment_new_id).exists()
    if qs_exists:
        return unique_payment_id_generator(instance)
    return payment_new_id
