# Generated by Django 4.1.2 on 2023-04-20 05:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0092_watersystemnode_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersystemflow',
            name='level',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.AddField(
            model_name='watersystemflow',
            name='part_of_flow',
            field=models.ForeignKey(blank=True, help_text='If this is a level-2 flow, then we indicate which level-1 flow this is part of', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.watersystemflow'),
        ),
        migrations.AlterField(
            model_name='watersystemnode',
            name='level',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='watersystemflow',
            unique_together={('identifier', 'category', 'level')},
        ),
    ]