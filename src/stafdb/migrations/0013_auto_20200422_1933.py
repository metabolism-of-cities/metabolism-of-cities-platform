# Generated by Django 3.0.3 on 2020-04-22 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stafdb', '0012_auto_20200422_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geocode',
            name='scheme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geocodes', to='stafdb.GeocodeScheme'),
        ),
    ]