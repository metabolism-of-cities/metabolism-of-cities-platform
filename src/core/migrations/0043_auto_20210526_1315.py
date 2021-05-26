# Generated by Django 3.1.2 on 2021-05-26 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20210525_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='cityloopsscareport',
            name='actors_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='actors_description_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='actors_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='indicators_table',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='indicators_table_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='land_use_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='land_use_description_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='land_use_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='population_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='population_description_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='population_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='recommendations',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='recommendations_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='sector_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='sector_description_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='status_quo',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='status_quo_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='upscaling',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cityloopsscareport',
            name='upscaling_html',
            field=models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True),
        ),
    ]