from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from users.s3_storage import S3_ProfileImage_Storage
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator, MaxLengthValidator


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

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class ProfileStatuses(models.TextChoices):
    ACTIVE = 'ACTIVE', _('ACTIVE')
    DELETED = 'DELETED', _('DELETED')
    REMOVED = 'REMOVED', _('REMOVED')


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
    status = models.CharField(_("Teacher Status"), null=True, choices=ProfileStatuses.choices, max_length=7,
                              help_text="Teacher Profile status", default=ProfileStatuses.ACTIVE)

    def save(self, *args, **kwargs):
        self.subdomain = self.subdomain.lower()
        super(TeacherProfile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Teacher Profile')
        verbose_name_plural = _('Teacher Profiles')


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


class PaymentTypes(models.TextChoices):
    STRIPE = 'STRIPE', _('Stripe payment')
    PAYPAL = 'PAYPAL', _('Paypal payment')
    BANK = 'BANK', _('Bank Account')


class PaymentAccounts(models.Model):
    """
    Data Associated to teacher payment accounts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    payment_type = models.CharField(_("payment type"), choices=PaymentTypes.choices, max_length=10,
                                    help_text="Type of payment account")
    info = models.JSONField(null=False, blank=False)

    class Meta:
        unique_together = ['payment_type', 'user']


class TeacherEarnings(models.Model):
    """
    Teacher earnings data
    """
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="earnings")
    amount = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=10)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Earning Data')
        verbose_name_plural = _('Earnings Data')


class TeacherPageVisits(models.Model):
    """
    Teacher earnings data
    """
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="page_visits")
    visits = models.PositiveBigIntegerField()
    visit_date = models.DateField(default=timezone.now().date)

    class Meta:
        verbose_name = _('Page Visit')
        verbose_name_plural = _('Page Visits')
        unique_together = ('teacher', 'visit_date')


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



