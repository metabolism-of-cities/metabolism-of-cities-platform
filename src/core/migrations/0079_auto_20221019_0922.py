# Generated by Django 3.1.2 on 2022-10-19 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0078_cityloopsucareport'),
    ]

    operations = [
        migrations.AddField(
            model_name='cityloopsucareport',
            name='references',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsucareport',
            name='references_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
    ]
