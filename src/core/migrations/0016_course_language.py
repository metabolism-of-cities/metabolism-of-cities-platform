# Generated by Django 3.1.2 on 2020-12-21 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20201221_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.language'),
        ),
    ]
