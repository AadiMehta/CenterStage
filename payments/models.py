from engine.models import Enrollment
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from engine.models import Enrollment
from users.models import PaymentAccounts, BillingProfile
# Create your models here.


class Payment(models.Model):
    payment_identifier = models.CharField(
        max_length=96, unique=True, verbose_name=_("identifier"))
    amount = models.DecimalField(
        decimal_places=2, max_digits=10, verbose_name=_('amount'))
    payment_amount_currency = models.CharField(
        max_length=10, verbose_name=_('payment amount currency'))
    foreign_amount = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=10, verbose_name=_("foreign amount"))
    foreign_currency = models.CharField(
        max_length=10, blank=True, null=True, verbose_name=_("foreign amount currency"))
    description = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("description"))
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created on"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated on"))

    class Meta:
        abstract = True


class LessonPayment(Payment):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE, related_name='lesson_payments')
    payment_account = models.ForeignKey(PaymentAccounts, on_delete=models.CASCADE, related_name='lesson_payments')
    info = models.JSONField(null=True)
    # enrollment = models.ManyToManyField(
    #     Enrollment, related_name="payments", on_delete=models.PROTECT, verbose_name=_("enrollment"))
    class Meta:
        verbose_name = _("Lesson Payment")
        verbose_name_plural = _("Lesson Payments")

    # @property
    # def currency(self):
    #     price = self.enrollment.price
    #     return price.get('currency')

    # @property
    # def lesson_slots(self):
    #     return self.enrollment.lessonslot.count()