from django.conf import settings
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
    price_per_session = models.IntegerField()
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
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['payment_type', 'user']


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
