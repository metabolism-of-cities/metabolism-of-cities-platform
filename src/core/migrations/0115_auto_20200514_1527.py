# Generated by Django 3.0.3 on 2020-05-14 15:27

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0114_badge_projects'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadsession',
            name='type',
            field=models.CharField(choices=[('shapefile', 'Shapefile'), ('flowdata', 'Material flow data'), ('stockdata', 'Material stock data')], default='shapefile', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='uploadfile',
            name='file',
            field=models.FileField(upload_to=core.models.upload_directory),
        ),
    ]