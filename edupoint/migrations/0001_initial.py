# Generated by Django 3.2.8 on 2021-11-25 16:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import edupoint.models
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True, unique=True, verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True, verbose_name='Course')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True, unique=True, verbose_name='Subject')),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
            },
        ),
        migrations.CreateModel(
            name='TestPaper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Title for test paper.', max_length=250, verbose_name='Title')),
                ('max_time', models.IntegerField(default=0, help_text='Maximum time for test to submit in seconds.', verbose_name='Max Time')),
                ('max_marks', models.IntegerField(default=0, help_text='Maximum marks for test.', verbose_name='Max Marks')),
                ('instructions', models.TextField(blank=True, help_text='Instructions to be followed during test by user.', verbose_name='Instructions')),
                ('slug', models.SlugField(blank=True, help_text='A user friendly url for test.', unique=True, verbose_name='URL')),
                ('roll_out', models.BooleanField(default=False, help_text='Paper is published or not.', verbose_name='Published')),
                ('random_order', models.BooleanField(blank=True, default=False, help_text='Display the questions in a random order or as they are set?', verbose_name='Random Order')),
                ('answers_at_end', models.BooleanField(default=False, help_text='Correct answer is NOT shown after question. Answers displayed at the end.', verbose_name='Show Answers')),
                ('single_attempt', models.BooleanField(default=False, help_text='If yes, only one attempt by a user will be permitted. Non users cannot sit this exam.', verbose_name='Single Attempt')),
                ('save_record', models.BooleanField(default=False, help_text='If yes, the result of each attempt by a user will be stored. Necessary for marking.', verbose_name='Save Record')),
                ('pass_mark', models.SmallIntegerField(blank=True, default=0, help_text='Percentage required to pass exam.', validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Pass Mark')),
                ('success_text', models.TextField(blank=True, help_text='Displayed if user passes.', verbose_name='Success Text')),
                ('fail_text', models.TextField(blank=True, help_text='Displayed if user fails.', verbose_name='Fail Text')),
                ('correct_marking', models.SmallIntegerField(blank=True, default=0, help_text='Marking on correct answer.', verbose_name='Correct Marking')),
                ('negative_marking', models.SmallIntegerField(blank=True, default=0, help_text='Marking on incorrect answer.', verbose_name='Negative Marking')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(help_text='Name of category.', null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.category', verbose_name='Category')),
                ('course', models.ForeignKey(help_text='Name of course.', null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.course', verbose_name='Course')),
                ('subject', models.ForeignKey(help_text='Name of subject.', null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.subject', verbose_name='Subject')),
            ],
            options={
                'verbose_name': 'Test Paper',
                'verbose_name_plural': 'Test Papers',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Sitting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_order', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Question Order')),
                ('question_list', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Question List')),
                ('incorrect_questions', models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Incorrect questions')),
                ('skipped_questions', models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Skipped questions')),
                ('current_score', models.IntegerField(verbose_name='Current Score')),
                ('complete', models.BooleanField(default=False, verbose_name='Complete')),
                ('user_answers', models.TextField(blank=True, default='{}', verbose_name='User Answers')),
                ('start', models.DateTimeField(auto_now_add=True, verbose_name='Start')),
                ('end', models.DateTimeField(blank=True, null=True, verbose_name='End')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edupoint.testpaper', verbose_name='Paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Sitting',
                'verbose_name_plural': 'User Sitting Record',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Enter question text.', max_length=2000, null=True, verbose_name='Question')),
                ('figure', models.ImageField(blank=True, help_text='Figure for question if any.', null=True, upload_to=edupoint.models.question_image_path, verbose_name='Question Figure')),
                ('explanation', models.TextField(blank=True, help_text='Explanation to be shown after the question has been answered.', max_length=2000, verbose_name='Explanation')),
                ('explanation_figure', models.ImageField(blank=True, help_text='Figure for explanation if any.', null=True, upload_to=edupoint.models.explanation_image_path, verbose_name='Explanation Figure')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.category', verbose_name='Category')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.course', verbose_name='Course')),
                ('paper', models.ManyToManyField(blank=True, help_text='Test paper name.', to='edupoint.TestPaper', verbose_name='Test Paper')),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='edupoint.subject', verbose_name='Subject')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
                'ordering': ['category'],
            },
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Category Score')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Progress',
                'verbose_name_plural': 'User Progress Record',
            },
        ),
    ]
