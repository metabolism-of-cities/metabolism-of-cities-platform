# Generated by Django 3.0.3 on 2020-04-26 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_journal_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
    ]