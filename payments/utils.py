
import datetime
import os
import random
import string

from django.utils import timezone
from django.utils.text import slugify


def random_string_generator(size=24, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    """
    This is for an order_id field
    """
    new_order_id = random_string_generator()

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(
        order_id=new_order_id).exists()
    if qs_exists:
        return unique_order_id_generator(instance)
    return new_order_id


def unique_payment_id_generator(instance):
    """
    This is for an order_id field
    """
    new_payment_identifier = random_string_generator()

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(
        payment_identifier=new_payment_identifier).exists()
    if qs_exists:
        return unique_payment_id_generator(instance)
    return new_payment_identifier
