# Generated by Django 3.0.3 on 2020-05-03 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0063_auto_20200503_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpagedesign',
            name='webpage',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='design', serialize=False, to='core.Record'),
        ),
    ]