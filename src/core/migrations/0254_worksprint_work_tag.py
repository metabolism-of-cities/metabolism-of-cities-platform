# Generated by Django 3.0.6 on 2020-08-20 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0253_video_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='worksprint',
            name='work_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Tag'),
        ),
    ]