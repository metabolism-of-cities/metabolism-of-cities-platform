# Generated by Django 3.0.3 on 2020-05-01 15:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20200501_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forummessage',
            name='date_created',
        ),
        migrations.AddField(
            model_name='record',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='DataViz',
        ),
    ]