# Generated by Django 3.1.2 on 2022-09-22 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_auto_20220909_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='is_public',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]