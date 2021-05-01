import uuid
import math
import datetime
import stripe
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from engine.models import LessonData, LessonSlots, Enrollment, EnrollmentChoices
from users.models import PaymentAccounts, BillingProfile, StudentProfile, PaymentTypes
from .utils import unique_order_id_generator
# Create your models here.


stripe.api_key = settings.STRIPE_SECRET_KEY

class OrderChoices(models.TextChoices):
    CREATED = 'created', _('created')
    PAID = 'paid', _('Paid')
    REFUNDED = 'refunded', _('refunded')


class OrderManagerQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by("-updated_at", "-created_at")

    def not_refunded(self):
        return self.exclude(status=OrderChoices.REFUNDED)

    def by_request(self, request, payment_type=PaymentTypes.STRIPE):
        billing_profile, created = BillingProfile.objects.new_or_get(
            request, payment_type=payment_type)
        return self.filter(billing_profile=billing_profile)

    def not_created(self):
        return self.exclude(status=OrderChoices.CREATED)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def new(self, validated_data):
        fields = validated_data
        model_obj = self.model.objects.create(**fields)
        return model_obj

    def get_order(self, fields):
        obj = self.get_queryset().filter(
            student=fields.get("student"),
            lesson=fields.get("lesson"),
            active=fields.get('active'),
            status=fields.get('status')
        ).first()
        return obj

    def update_obj(self, instance, fields):
        model_obj = instance
        for key, value in fields.items():
            setattr(model_obj, key, value)
        model_obj.save()
        return model_obj

    def new_or_get(self, fields):
        created = False
        qs = self.get_queryset().filter(
            student=fields.get("student"),
            lesson=fields.get("lesson"),
            active=True,
            status=OrderChoices.CREATED
        )
        if qs.exists():
            obj = qs.first()
        else:
            obj = self.model.objects.create(**fields)
            created = True
        return obj, created


class LessonOrder(models.Model):
    order_id = models.CharField(
        max_length=120, blank=True, verbose_name=_("order id"))
    student = models.ForeignKey(
        StudentProfile, related_name='orders', on_delete=models.CASCADE, verbose_name=_("student profile"))
    lesson = models.ForeignKey(
        LessonData, on_delete=models.CASCADE, related_name="orders", verbose_name=_("lesson"))
    lesson_slots = models.ManyToManyField(
        LessonSlots, blank=True, related_name="orders", verbose_name=_("lesson slots"))
    status = models.CharField(max_length=20, default=OrderChoices.CREATED,
                              choices=OrderChoices.choices, verbose_name=_("status"))
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True, verbose_name=_("active"))
    info = models.JSONField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

    objects = OrderManager()

    class Meta:
        verbose_name = _("Lesson Order")
        verbose_name_plural = _("Lesson Orders")
        ordering = ['-created_at', '-updated_at']

    def update_total(self):
        price = self.lesson.price['value']
        total_slots = self.lesson_slots.count()
        new_total = total_slots * int(price)
        self.total = new_total
        self.save()
        return new_total

    def mark_paid(self):
        if self.status != OrderChoices.PAID:
            self.status = OrderChoices.PAID
            self.active = False
            self.save()
        return self.status

    @property
    def is_completed(self):
        return self.status == OrderChoices.PAID and self.active == False

    def update_enrollments(self):
        lesson_slots = self.lesson_slots.all()
        for lesson_slot in lesson_slots:
            enrollment = Enrollment.objects.filter(
                student=self.student, lesson=self.lesson, lessonslot=lesson_slot).first()
            if not enrollment:
                enrollment = Enrollment.objects.create(student=self.student, lesson=self.lesson, lessonslot=lesson_slot,
                                                       status=EnrollmentChoices.ACTIVE)

        return Enrollment.objects.filter(lesson=self.lesson, student=self.student).count()

# ***************** Lesson Order Models Signals ******************
# TODO: move signals to signals.py

@receiver(pre_save, sender=LessonOrder)
def pre_save_order_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

class PaymentIntentManager(models.Manager):
    def get_teacher_stripe_account(self, lesson):
        user = lesson.creator.user
        stripe_account = user.get_stripe_account()
        return stripe_account
    
    def calculate_order_amount(self, lesson, order_obj):
        """
        Calculate the order total on the server to prevent
        A positive integer representing how much to charge in the smallest currency unit
        e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency
        """
        total_slots = order_obj.lesson_slots.count()
        price = lesson.price.get('value')
        order_amount = total_slots * int(price)
        return order_amount * 100
    
    def calculate_application_fee_amount(self, amount):
        # Take a 10% cut.
        application_fee = 0.1
        return int(application_fee * amount)

    def do(self, request, order_obj):
        user = request.user
        billing_profile, is_created = BillingProfile.objects.new_or_get(request, payment_type=PaymentTypes.STRIPE)
        lesson = order_obj.lesson

        try:
            # Create a PaymentIntent with the order amount, currency, and transfer destination
            teacher_stripe_account = self.get_teacher_stripe_account(lesson)
            total_amount = self.calculate_order_amount(lesson, order_obj)
            application_fee_amount = self.calculate_application_fee_amount(total_amount)

            stripe_payment_intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency=lesson.price.get('currency'),
                transfer_data={'destination': teacher_stripe_account.account_id},
                customer=billing_profile.customer_id,
                metadata={'order_id': order_obj.order_id, 'lesson_id': lesson.lesson_uuid},
                application_fee_amount=application_fee_amount
            )
            new_payment_intent_obj = self.model.objects.create(
                billing_profile=billing_profile,
                stripe_id=stripe_payment_intent.id,
                order=order_obj
            )
            return stripe_payment_intent, True # intent, created
        except Exception as e:
            return e, False # error, created


class PaymentIntent(models.Model):
    """
    Stripe PaymentIntent for Lesson Order
    """
    billing_profile = models.ForeignKey(
        BillingProfile, related_name='payment_intent', on_delete=models.CASCADE, verbose_name=_("billing profile"))
    stripe_id = models.CharField(max_length=120, verbose_name=_("stripe id"))
    order =  models.ForeignKey(
        LessonOrder, related_name='payment_intent', on_delete=models.CASCADE, verbose_name=_("order"))
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    info = models.JSONField(null=True)
    description = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("description"))
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created on"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("updated on"))

    objects = PaymentIntentManager()
    class Meta:
        verbose_name = _("Lesson Payment")
        verbose_name_plural = _("Lesson Payments")
