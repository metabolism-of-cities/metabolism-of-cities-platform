# Generated by Django 3.1.2 on 2022-09-30 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_auto_20220930_2022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='data',
            old_name='end',
            new_name='date_end',
        ),
        migrations.RenameField(
            model_name='data',
            old_name='start',
            new_name='date_start',
        ),
        migrations.RenameField(
            model_name='data',
            old_name='timeframe_name',
            new_name='dates_label',
        ),
    ]
