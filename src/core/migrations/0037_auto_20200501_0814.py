# Generated by Django 3.0.3 on 2020-05-01 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_dataviz'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibraryItemAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.LibraryItem')),
                ('people', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.People')),
            ],
            options={
                'db_table': 'core_library_authors',
            },
        ),
        migrations.AddField(
            model_name='libraryitem',
            name='authors',
            field=models.ManyToManyField(through='core.LibraryItemAuthor', to='core.People'),
        ),
    ]