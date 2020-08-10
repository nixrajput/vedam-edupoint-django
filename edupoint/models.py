from django.db import models
import datetime
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser


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
    img = models.ImageField(upload_to=image_path, verbose_name='profile image', blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profile_picture'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Course(models.Model):
    title = models.CharField(verbose_name='course name', max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Class(models.Model):
    title = models.CharField(verbose_name='class name', max_length=150, unique=True)
    course_name = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_name_for_class'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Subject(models.Model):
    course_name = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_name_for_subject'
    )

    class_name = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_name_for_subject'
    )

    title = models.CharField(verbose_name='subject name', max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.course_name} - {self.class_name}"


class Question(models.Model):
    subject_name = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subject_name_for_question'
    )

    qstn_no = models.IntegerField(verbose_name='question number', unique=True, blank=True, null=True)
    question_text = models.TextField(verbose_name='question text')
    correct_ans = models.CharField
    option1 = models.CharField(verbose_name='option 1 for answer', max_length=150)
    option2 = models.CharField(verbose_name='option 2 for answer', max_length=150)
    option3 = models.CharField(verbose_name='option 3 for answer', max_length=150)
    option4 = models.CharField(verbose_name='option 4 for answer', max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question_text}"


