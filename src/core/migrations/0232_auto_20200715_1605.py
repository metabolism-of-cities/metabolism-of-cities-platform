# Generated by Django 3.0.6 on 2020-07-15 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0231_remove_libraryitem_files'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='attachments',
        ),
        migrations.AlterField(
            model_name='document',
            name='attached_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='core.Record'),
        ),
    ]