# Generated by Django 3.0.6 on 2020-09-30 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0277_auto_20200930_0856'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryitem',
            name='geocodes',
            field=models.ManyToManyField(blank=True, to='core.Geocode'),
        ),
    ]