# Generated by Django 3.0.3 on 2020-03-07 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200307_0452'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='url',
            field=models.SlugField(allow_unicode=True, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('site', 'url'), name='site_url'),
        ),
    ]