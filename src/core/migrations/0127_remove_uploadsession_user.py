# Generated by Django 3.0.3 on 2020-05-19 07:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0126_news_include_in_timeline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadsession',
            name='user',
        ),
    ]