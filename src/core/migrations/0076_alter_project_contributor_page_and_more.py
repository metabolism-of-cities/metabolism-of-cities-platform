# Generated by Django 4.1.2 on 2022-10-07 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_auto_20220930_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='contributor_page',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='support_page',
            field=models.TextField(blank=True, null=True),
        ),
    ]
