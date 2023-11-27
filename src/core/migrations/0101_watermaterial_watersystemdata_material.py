# Generated by Django 4.1.2 on 2023-11-21 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0100_cityloopshandbookpage_alter_watersystemfile_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_french', models.CharField(max_length=255)),
                ('name_english', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name_french'],
            },
        ),
        migrations.AddField(
            model_name='watersystemdata',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.watermaterial'),
        ),
    ]