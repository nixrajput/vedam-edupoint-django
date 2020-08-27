# Generated by Django 3.1 on 2020-08-27 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edupoint', '0002_auto_20200825_0102'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testpaper',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Test Paper', 'verbose_name_plural': 'Test Papers'},
        ),
        migrations.AlterField(
            model_name='testpaper',
            name='slug',
            field=models.SlugField(blank=True, editable=False, help_text='A user friendly url for test.', unique=True, verbose_name='URL'),
        ),
    ]
