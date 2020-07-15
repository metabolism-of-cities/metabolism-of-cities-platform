# Generated by Django 3.0.6 on 2020-07-01 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0210_auto_20200701_0606'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='badges',
            field=models.ManyToManyField(blank=True, to='core.Badge'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='code',
            field=models.CharField(blank=True, db_index=True, help_text='Do not change, this is used in the code to verify if people have the right permission level', max_length=20, null=True),
        ),
    ]