# Generated by Django 3.1.2 on 2021-03-07 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20210307_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitemtype',
            name='group',
            field=models.CharField(blank=True, choices=[('academic', 'Academic'), ('reports', 'Reports'), ('data', 'Data'), ('multimedia', 'Multimedia'), ('other', 'Other')], max_length=20, null=True),
        ),
    ]
