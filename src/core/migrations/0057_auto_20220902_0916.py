# Generated by Django 3.1.2 on 2022-09-02 09:16

from django.db import migrations, models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_libraryitemtype_ris_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='has_private_documents',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='project',
            name='screenshot',
            field=stdimage.models.StdImageField(blank=True, force_min_size=False, help_text='1280x1024 is best - do not include browser tabs/menus', null=True, upload_to='project_screenshots', variations={'large': (1280, 1024), 'medium': (510, 510), 'thumbnail': (350, 350)}),
        ),
        migrations.AlterField(
            model_name='record',
            name='image',
            field=stdimage.models.StdImageField(blank=True, force_min_size=False, null=True, upload_to='records', variations={'large': (1280, 1024), 'thumbnail': (480, 480)}),
        ),
        migrations.AlterField(
            model_name='socialmedia',
            name='image',
            field=stdimage.models.StdImageField(blank=True, force_min_size=False, null=True, upload_to='socialmedia', variations={'large': (1280, 1024), 'thumbnail': (480, 480)}),
        ),
        migrations.AlterField(
            model_name='webpagedesign',
            name='header_image',
            field=stdimage.models.StdImageField(blank=True, force_min_size=False, null=True, upload_to='header_image', variations={'huge': (2560, 1440), 'large': (1280, 1024), 'thumbnail': (480, 480)}),
        ),
    ]
