# Generated by Django 3.0.3 on 2020-04-28 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_libraryitem_spaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='slug',
            field=models.CharField(db_index=True, default='test', max_length=255),
            preserve_default=False,
        ),
    ]