# Generated by Django 3.1.2 on 2021-02-28 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20210228_1950'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workcategory',
            options={'ordering': ['id']},
        ),
    ]