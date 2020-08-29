import datetime
import os
import uuid

import django.contrib.auth.validators
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUser(AbstractUser):
    userId = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    dob = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("DOB"),
        help_text=_("Date of birth of user.")
    )
    is_valid = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("User is verified or not.")
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("All Users")


def image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    today = datetime.datetime.now()
    y = today.strftime('%Y')
    m = today.strftime('%m')
    d = today.strftime('%d')

    rand_str = uuid.uuid4()
    return 'profile_img/{year}{month}{date}/{user_id}/{random_string}{ext}' \
        .format(year=y, month=m, date=d, user_id=instance.user.userId, random_string=rand_str, ext=file_extension)


class UserProfileImage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("User")
    )

    img = models.ImageField(
        upload_to=image_path,
        null=True,
        verbose_name='Profile Picture',
        help_text=_("User's profile picture.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile Picture")
        verbose_name_plural = _("Profile Pictures")

    def __str__(self):
        return self.img.name


class ContactUs(models.Model):
    full_name = models.CharField(
        max_length=150,
        null=True,
        verbose_name=_("Full Name")
    )
    subject = models.CharField(
        max_length=150,
        null=True,
        verbose_name=_("Email Subject")
    )
    email = models.EmailField(
        max_length=254,
        null=True,
        verbose_name=_("Email Address")
    )
    comment = models.TextField(
        null=True,
        verbose_name=_("Email Content")
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Contact Form")
        verbose_name_plural = _("Contact Forms")

    def __str__(self):
        return self.subject


def admin_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    today = datetime.datetime.now()
    y = today.strftime('%Y')
    m = today.strftime('%m')
    d = today.strftime('%d')

    rand_str = uuid.uuid4()
    return 'admin_img/{year}{month}{date}/{user_id}/{random_string}{ext}' \
        .format(year=y, month=m, date=d, user_id=instance.userId, random_string=rand_str, ext=file_extension)


class TeamMember(models.Model):
    userId = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
    )
    first_name = models.CharField(
        max_length=150,
        null=True,
        verbose_name=_('First Name'),
        help_text=_("First name of team member.")
    )
    last_name = models.CharField(
        max_length=150,
        null=True,
        verbose_name=_('Last Name'),
        help_text=_("Last name of team member.")
    )
    email = models.EmailField(
        null=True,
        unique=True,
        verbose_name=_('Email Address'),
        help_text=_("Email address of team member.")
    )
    username = models.CharField(
        max_length=150,
        null=True,
        unique=True,
        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
        verbose_name=_("Username"),
        help_text=_("Username of team member.")
    )
    dob = models.DateField(
        null=True,
        verbose_name=_("DOB"),
        help_text=_("Date of birth of team member.")
    )
    img = models.ImageField(
        upload_to=admin_image_path,
        null=True,
        blank=True,
        verbose_name=_("Profile Picture"),
        help_text=_("Profile picture of team member.")
    )
    about = models.TextField(
        null=True,
        verbose_name=_("About"),
        help_text=_("About text for team member.")
    )
    designation = models.CharField(
        max_length=150,
        null=True,
        verbose_name=_("Designation"),
        help_text=_("Current designation of team member.")
    )

    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")

    def __str__(self):
        return self.username
