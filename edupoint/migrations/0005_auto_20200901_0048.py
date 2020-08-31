# Generated by Django 3.1 on 2020-08-31 19:18

from django.db import migrations, models
import edupoint.models


class Migration(migrations.Migration):

    dependencies = [
        ('edupoint', '0004_auto_20200827_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='explanation_figure',
            field=models.ImageField(blank=True, help_text='Figure for explanation if any.', null=True, upload_to=edupoint.models.explanation_image_path, verbose_name='Explanation Figure'),
        ),
        migrations.AlterField(
            model_name='question',
            name='figure',
            field=models.ImageField(blank=True, help_text='Figure for question if any.', null=True, upload_to=edupoint.models.question_image_path, verbose_name='Question Figure'),
        ),
    ]