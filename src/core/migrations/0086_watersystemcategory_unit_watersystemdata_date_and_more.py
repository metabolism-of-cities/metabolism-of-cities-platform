# Generated by Django 4.1.2 on 2023-04-11 09:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_watersystemfile_is_processed_watersystemdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersystemcategory',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.unit'),
        ),
        migrations.AddField(
            model_name='watersystemdata',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='watersystemdata',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='core.watersystemfile'),
        ),
    ]