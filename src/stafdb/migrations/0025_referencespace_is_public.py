# Generated by Django 3.0.3 on 2020-05-08 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stafdb', '0024_auto_20200429_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='referencespace',
            name='is_public',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]