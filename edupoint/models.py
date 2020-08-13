from django.db import models
import datetime
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class CustomUser(AbstractUser):
    userId = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dob = models.DateField(blank=True, null=True, verbose_name='date of birth')
    is_valid = models.BooleanField(default=False, verbose_name='validation status')


def image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    today = datetime.datetime.now()
    y = today.strftime('%Y')
    m = today.strftime('%m')
    d = today.strftime('%d')

    rand_str = uuid.uuid4()
    return 'profile_img/{year}/{month}/{date}/{user_id}/{random_string}{ext}' \
        .format(year=y, month=m, date=d, user_id=instance.user.userId, random_string=rand_str, ext=file_extension)


class UserProfileImage(models.Model):
    img = models.ImageField(upload_to=image_path, verbose_name='profile image', null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_picture',
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class TestPaper(models.Model):
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=150)
    category = models.CharField(max_length=150)
    subject = models.CharField(max_length=150)
    max_time = models.IntegerField(default=0)
    max_marks = models.IntegerField(default=0)
    instructions = models.TextField(blank=True)
    slug = models.SlugField(blank=True)
    roll_out = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp', ]
        verbose_name_plural = "TestPaper"

    def __str__(self):
        return self.name


class Question(models.Model):
    paper = models.ForeignKey(
        TestPaper,
        on_delete=models.CASCADE,
        null=True,
    )
    text = models.TextField(null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
    )
    option = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option


class TestUser(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
    )
    paper = models.ForeignKey(
        TestPaper,
        on_delete=models.CASCADE,
        null=True,
    )
    score = models.IntegerField(default=0)
    attempted = models.BooleanField(default=False)
    date_attempted = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class UsersAnswer(models.Model):
    test_user = models.ForeignKey(
        TestUser,
        on_delete=models.CASCADE,
        null=True,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return self.question.text


@receiver(pre_save, sender=TestPaper)
def slugify_name(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name)
