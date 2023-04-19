# Generated by Django 4.1.2 on 2023-04-18 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0089_alter_watersystemdata_flow'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterSystemNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('identifier', models.PositiveSmallIntegerField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.watersystemcategory')),
                ('entry_flows', models.ManyToManyField(related_name='entry', to='core.watersystemflow')),
                ('exit_flows', models.ManyToManyField(related_name='exit', to='core.watersystemflow')),
            ],
        ),
    ]