# Generated by Django 3.1.2 on 2021-06-08 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20210527_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='cityloopsscareport',
            name='gaps',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='gaps_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='matrix',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='matrix_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
    ]
