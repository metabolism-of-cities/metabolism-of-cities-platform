# Generated by Django 3.1.2 on 2022-09-27 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0068_auto_20220927_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryitem',
            name='json',
            field=models.JSONField(blank=True, null=True),
        ),
    ]