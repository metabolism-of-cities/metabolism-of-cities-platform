# Generated by Django 4.1.2 on 2022-10-17 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_alter_document_attached_to'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityLoopsUCAReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(blank=True, null=True)),
                ('summary_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('space_population', models.IntegerField(blank=True, null=True)),
                ('space_size', models.IntegerField(blank=True, null=True)),
                ('nuts3_population', models.IntegerField(blank=True, null=True)),
                ('nuts3_size', models.IntegerField(blank=True, null=True)),
                ('nuts2_population', models.IntegerField(blank=True, null=True)),
                ('nuts2_size', models.IntegerField(blank=True, null=True)),
                ('country_population', models.IntegerField(blank=True, null=True)),
                ('country_size', models.IntegerField(blank=True, null=True)),
                ('population_description', models.TextField(blank=True, null=True)),
                ('population_description_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('land_use_description', models.TextField(blank=True, null=True)),
                ('land_use_description_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('space_gdp', models.PositiveBigIntegerField(blank=True, null=True)),
                ('space_employees', models.IntegerField(blank=True, null=True)),
                ('nuts3_gdp', models.PositiveBigIntegerField(blank=True, null=True)),
                ('nuts3_employees', models.IntegerField(blank=True, null=True)),
                ('nuts2_gdp', models.PositiveBigIntegerField(blank=True, null=True)),
                ('nuts2_employees', models.IntegerField(blank=True, null=True)),
                ('country_gdp', models.PositiveBigIntegerField(blank=True, null=True)),
                ('country_employees', models.IntegerField(blank=True, null=True)),
                ('econ_description', models.TextField(blank=True, null=True)),
                ('econ_description_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('domestic_extraction', models.TextField(blank=True, null=True)),
                ('domestic_extraction_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('imports_exports', models.TextField(blank=True, null=True)),
                ('imports_exports_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('consumption', models.TextField(blank=True, null=True)),
                ('consumption_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('waste', models.TextField(blank=True, null=True)),
                ('waste_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('typologies', models.TextField(blank=True, null=True)),
                ('typologies_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('stock', models.TextField(blank=True, null=True)),
                ('stock_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('indicator_table', models.TextField(blank=True, null=True)),
                ('indicator_table_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('indicators', models.TextField(blank=True, null=True)),
                ('indicators_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('matrix', models.TextField(blank=True, null=True)),
                ('matrix_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('quality', models.TextField(blank=True, null=True)),
                ('quality_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('gaps', models.TextField(blank=True, null=True)),
                ('gaps_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('status_quo', models.TextField(blank=True, null=True)),
                ('status_quo_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('recommendations', models.TextField(blank=True, null=True)),
                ('recommendations_html', models.TextField(blank=True, help_text='Do not edit... auto-generated by the system', null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.referencespace')),
                ('land_use_dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uca_land_use', to='core.libraryitem')),
                ('materials_dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uca_materials', to='core.libraryitem')),
                ('population_dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uca_population', to='core.libraryitem')),
                ('stock_map_dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_map', to='core.libraryitem')),
            ],
            options={
                'ordering': ['city'],
            },
        ),
    ]
