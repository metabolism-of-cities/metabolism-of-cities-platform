# Generated by Django 3.0.6 on 2020-06-24 06:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0184_auto_20200624_0529'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicproject',
            name='part_of_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Project'),
        ),
    ]