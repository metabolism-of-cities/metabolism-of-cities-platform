# Generated by Django 3.0.3 on 2020-04-29 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20200429_0452'),
        ('stafdb', '0022_remove_referencespace_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('activities', models.ManyToManyField(to='stafdb.Activity')),
                ('photo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Photo')),
            ],
        ),
        migrations.CreateModel(
            name='ReferenceSpaceSector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stafdb.Sector')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sectors', to='stafdb.ReferenceSpace')),
            ],
        ),
    ]