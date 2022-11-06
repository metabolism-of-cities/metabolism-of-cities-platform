# Generated by Django 3.1.2 on 2022-09-27 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_auto_20220927_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryitem',
            name='json_drilldown',
            field=models.JSONField(blank=True, help_text='Here we store the JSON representation needed for drill-down data visualizations', null=True),
        ),
    ]