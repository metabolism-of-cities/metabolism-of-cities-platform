# Generated by Django 3.1.2 on 2021-02-19 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20210217_0939'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cityloopsindicatorvalue',
            old_name='period',
            new_name='area',
        ),
        migrations.RemoveField(
            model_name='cityloopsindicatorvalue',
            name='reference',
        ),
        migrations.AddField(
            model_name='cityloopsindicatorvalue',
            name='completed',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsindicatorvalue',
            name='last_update',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsindicatorvalue',
            name='period_from',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsindicatorvalue',
            name='period_to',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]