# Generated by Django 3.0.6 on 2020-07-02 10:50

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0216_auto_20200702_0653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('file', models.FileField(blank=True, null=True, upload_to='files')),
                ('original_name', models.CharField(max_length=255)),
            ],
            bases=('core.record',),
            managers=[
                ('objects_unfiltered', django.db.models.manager.Manager()),
            ],
        ),
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.AlterField(
            model_name='message',
            name='attachments',
            field=models.ManyToManyField(blank=True, to='core.Attachment'),
        ),
    ]