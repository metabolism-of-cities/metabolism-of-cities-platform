# Generated by Django 3.1.2 on 2021-02-26 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20210224_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('show_in_tasklist', models.BooleanField(db_index=True, default=True)),
                ('icon', models.CharField(blank=True, help_text='Only include the icon name, not fa- classes --- see https://fontawesome.com/icons?d=gallery', max_length=50, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='workactivity',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.workcategory'),
        ),
    ]
