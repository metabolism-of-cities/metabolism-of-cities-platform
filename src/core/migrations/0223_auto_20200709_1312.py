# Generated by Django 3.0.6 on 2020-07-09 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0222_auto_20200708_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitem',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]