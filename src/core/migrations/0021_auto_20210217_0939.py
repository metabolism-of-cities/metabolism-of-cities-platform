# Generated by Django 3.1.2 on 2021-02-17 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20210215_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialdemand',
            name='end_date',
            field=models.DateField(blank=True, help_text="The end date is optional, leave blank if it's open ended", null=True),
        ),
    ]
