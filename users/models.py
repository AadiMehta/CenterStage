import stripe
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import status

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from users.s3_storage import S3_ProfileImage_Storage
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator, MaxLengthValidator

from zoom.serializer import ZoomAuthResponseSerializer
from zoom.utils import zoomclient


stripe.api_key = settings.STRIPE_SECRET_KEY

class UserTypes(models.TextChoices):
    CREATOR_USER = 'CR', _('Creator User')
    STUDENT_USER = 'ST', _('Student User')
    # CRESTU_USER = 'CS', _('Both Creator and Student User')
    ADMIN_USER = 'AD', _('Admin User')


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, user_type, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_creator_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, "CR", **extra_fields)

    def create_student_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, "ST", **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, "AD", **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User Table, which will provide login functionality
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Required:
        email
        password
        first_name
        last_name
        phone_no
    """
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    phone_no = PhoneNumberField(unique=True, null=True)
    user_type = models.CharField(_("user type"), choices=UserTypes.choices, max_length=3,
                                 help_text="Type of user")

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    last_login_ip = models.GenericIPAddressField(_('last login ip'), blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def get_user_type(self):
        """Returns the type of the user"""
        return self.get_user_type_display()

    @property
    def is_zoom_linked(self):
        """Returns boolean if user has connected zoom"""
        try:
            account = self.accounts.get(account_type=AccountTypes.ZOOM_VIDEO)
            return self.get_access_token(account)
        except Accounts.DoesNotExist:
            return False
    
    def get_stripe_account(self):
        """Returns stripe account of teacher"""
        try:
            account = self.payment_account.get(payment_type=PaymentTypes.STRIPE, active=True)
            return account
        except PaymentAccounts.DoesNotExist:
            return False
    
    def get_stripe_billing_profile(self):
        """Returns stripe customer account of student"""
        try:
            account = BillingProfile.objects.get_or_create(user=self, payment_type=PaymentTypes.STRIPE)
            return account
        except Exception as e:
            return False

    @staticmethod
    def get_access_token(account):
        expire_time = account.info.get('expires_time')
        if expire_time:
            expire_time = datetime.strptime(expire_time, '%Y-%m-%dT%H:%M:%S')
            if expire_time > timezone.now():
                # If expire time is greater than current time then return
                return account.info.get('access_token')

        # If token is expired then refresh token
        refresh_token = account.info.get('refresh_token')
        resp = zoomclient.refresh_token(refresh_token)
        if resp.status_code == status.HTTP_200_OK:
            access_info = resp.json()
            serializer = ZoomAuthResponseSerializer(data=access_info)
            serializer.is_valid(raise_exception=True)
            expires_in = serializer.validated_data.get('expires_in')
            expire_time = timezone.now() + timezone.timedelta(seconds=expires_in)
            serializer.validated_data['expire_time'] = expire_time.strftime('%Y-%m-%dT%H:%M:%S')

            account.info = serializer.validated_data
            account.save()
            return True
        else:
            account.delete()
            return False

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class ProfileStatuses(models.TextChoices):
    ACTIVE = 'ACTIVE', _('ACTIVE')
    DELETED = 'DELETED', _('DELETED')
    REMOVED = 'REMOVED', _('REMOVED')


class RecommendationChoices(models.TextChoices):
    LESSON_QUALITY = 'LESSON_QUALITY', _('LESSON_QUALITY')
    LESSON_CONTENT = 'LESSON_CONTENT', _('LESSON_CONTENT')
    LESSON_STRUCTURE = 'LESSON_STRUCTURE', _('LESSON_STRUCTURE')
    TEACHER_HELPFULNESS = 'TEACHER_HELPFULNESS', _('TEACHER_HELPFULNESS')
    TEACHER_COMMUNICATION = 'TEACHER_COMMUNICATION', _('TEACHER_COMMUNICATION')
    TEACHER_KNOWLEDGE = 'TEACHER_KNOWLEDGE', _('TEACHER_KNOWLEDGE')


class TeacherProfile(models.Model):
    """
    Additional data associated with the teacher user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile_data")
    subdomain = models.CharField(_('Domain Prefix'), max_length=32, unique=True,
                                 validators=[MinLengthValidator(4), MaxLengthValidator(32)])
    profile_image = models.ImageField(_("profile image"), storage=S3_ProfileImage_Storage(), null=True)
    year_of_experience = models.IntegerField(_('years of experience'), null=True, validators=[MinValueValidator(0),
                                                                                              MaxValueValidator(100)])
    profession = models.CharField(_("Profession"), max_length=64, validators=[MinLengthValidator(4)])
    bio = models.TextField(_('Bio for Teacher'), null=True, blank=True)
    intro_video = models.URLField(max_length=200, null=True, blank=True)
    verified = models.BooleanField(_('Teacher Verified'), default=False)
    status = models.CharField(_("Teacher Status"), null=True, choices=ProfileStatuses.choices, max_length=7,
                              help_text="Teacher Profile status", default=ProfileStatuses.ACTIVE)

    def save(self, *args, **kwargs):
        self.subdomain = self.subdomain.lower()
        super(TeacherProfile, self).save(*args, **kwargs)

    def get_teacher_full_url(self):
        return "{0}://{1}.{2}".format(settings.SCHEME, self.subdomain, settings.SITE_URL)

    class Meta:
        verbose_name = _('Teacher Profile')
        verbose_name_plural = _('Teacher Profiles')


class PersonalCoachingEnabled(models.Model):
    """
    Check if personal coaching is enabled
    """
    teacher = models.OneToOneField(TeacherProfile, on_delete=models.CASCADE, related_name="personal_coaching")
    duration = models.CharField(max_length=64)
    price_per_session = models.JSONField(null=False)
    free_sessions = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])


class AccountTypes(models.TextChoices):
    ZOOM_VIDEO = 'ZOOM', _('Zoom Video')
    GOOGLE_CALENDAR = 'GOOGLE_CALENDAR', _('GOOGLE_CALENDAR')
    TEAMS = 'TEAMS', _('Teams')


class Accounts(models.Model):
    """
    Data Associated to Social Accounts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    account_type = models.CharField(_("account type"), choices=AccountTypes.choices, max_length=30,
                                    help_text="Type of account")
    info = models.JSONField(null=True)
    token_updated_on = models.DateTimeField(auto_now=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'account_type')


class PaymentTypes(models.TextChoices):
    STRIPE = 'STRIPE', _('Stripe payment')
    PAYPAL = 'PAYPAL', _('Paypal payment')
    BANK = 'BANK', _('Bank Account')


class PaymentAccounts(models.Model):
    """
    Data Associated to teacher payment accounts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_account')
    payment_type = models.CharField(_('payment type'), max_length=10, choices=PaymentTypes.choices, default=PaymentTypes.STRIPE, help_text='Type of payment account')
    account_id = models.CharField(_('account id'), null=True, blank=True, max_length=120, help_text=_('account ID in payment gateway'))
    info = models.JSONField(null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['account_id', 'user']


class TeacherEarnings(models.Model):
    """
    Teacher earnings data
    """
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="earnings")
    amount = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=10)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Earning Data')
        verbose_name_plural = _('Earnings Data')


class TeacherPageVisits(models.Model):
    """
    Teacher earnings data

    TODO need to partition data based on month and year
    """
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="page_visits")
    visits = models.PositiveBigIntegerField(default=1)
    visit_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _('Page Visit')
        verbose_name_plural = _('Page Visits')
        unique_together = ('teacher', 'visit_date')

    @staticmethod
    def update_teacher_visit(teacher):
        # TODO move this to redis + cron to improve performance
        tpv, created = TeacherPageVisits.objects.get_or_create(teacher=teacher, visit_date=timezone.now().date())
        if not created:
            tpv.visits = tpv.visits + 1
            tpv.save()


class TeacherRating(models.Model):
    """
    Teacher Rating Model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rated")
    rate = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5.0)],)
    review = models.CharField(_("Review"), max_length=256)
    added_on = models.DateTimeField(auto_now_add=True)


class TeacherRecommendations(models.Model):
    """
    Teacher Recommendations Model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="recommendations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recommended")
    recommendation_type = models.CharField(_("Type of Recommendation"), choices=RecommendationChoices.choices, max_length=30)
    added_on = models.DateTimeField(auto_now_add=True)


class TeacherFollow(models.Model):
    """
    Teacher Follow Model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="followers")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")
    added_on = models.DateTimeField(auto_now_add=True)


class TeacherLike(models.Model):
    """
    Teacher Like Model
    """
    creator = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked")
    added_on = models.DateTimeField(auto_now_add=True)


# ***************** Student Models ******************


class StudentProfile(models.Model):
    """
    Additional data associated with the teacher user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile_data")
    bio = models.TextField(_('Student Bio'), null=True, blank=True)
    profile_image = models.ImageField(_("profile image"), storage=S3_ProfileImage_Storage(), null=True)
    status = models.CharField(_("Student Profile Status"), null=True, choices=ProfileStatuses.choices, max_length=7,
                              help_text="Student Profile status", default=ProfileStatuses.ACTIVE)

    class Meta:
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')


class BillingProfileManager(models.Manager):
    def new_or_get(self, request, payment_type=PaymentTypes.STRIPE):
        user = request.user
        obj, created = self.model.objects.get_or_create(user=user, payment_type=payment_type)
        return obj, created
    
class BillingProfile(models.Model):
    """
    Data Associated to student billing accounts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_profile')
    payment_type = models.CharField(_('payment type'), max_length=10, choices=PaymentTypes.choices, default=PaymentTypes.STRIPE, help_text='Type of payment account')
    customer_id = models.CharField(_('customer id'), null=True, blank=True, max_length=120, help_text=_('customer ID in payment gateway'))
    info = models.JSONField(null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BillingProfileManager()

    class Meta:
        unique_together = ['customer_id', 'user']


# ***************** Student Models Signals ******************
# TODO: move signals to signals.py

@receiver(post_save, sender=StudentProfile)
def student_created_receiver(sender, instance, created, *args, **kwargs):
    """
    create billing profile for student
    """
    if created and instance.user:
        BillingProfile.objects.get_or_create(
            user=instance.user, payment_type=PaymentTypes.STRIPE)


@receiver(pre_save, sender=BillingProfile)
def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    """
    create customer id in payment gateway - stripe or braintree
    """
    if not instance.customer_id and instance.user:
        if instance.payment_type == PaymentTypes.STRIPE:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.create(
                email=instance.user.email
            )
            instance.customer_id = customer.id
            instance.info = customer
