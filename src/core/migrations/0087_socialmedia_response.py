# Generated by Django 3.0.3 on 2020-05-08 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_auto_20200508_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmedia',
            name='response',
            field=models.TextField(blank=True, null=True),
        ),
    ]