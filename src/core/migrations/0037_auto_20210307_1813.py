# Generated by Django 3.1.2 on 2021-03-07 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20210303_0922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitemtype',
            name='group',
            field=models.CharField(blank=True, choices=[('academic', 'Academic'), ('theses', 'Theses'), ('reports', 'Reports'), ('multimedia', 'Multimedia'), ('other', 'Other')], max_length=20, null=True),
        ),
    ]
