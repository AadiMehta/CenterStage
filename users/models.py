from django.db import models
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


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

    def create_admin_user(self, email, password, **extra_fields):
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
    phone_no = models.CharField(_('contact number'), max_length=16, unique=True, null=True)
    user_type = models.CharField(_("user type"), choices=UserTypes.choices, max_length=3,
                                 help_text="Type of user")

    profile_image = models.ImageField(_("profile image"), null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

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
        return self.user_type.label

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class TeacherUser(models.Model):
    """
    Additional data associated with the teacher user
    """
    pass
