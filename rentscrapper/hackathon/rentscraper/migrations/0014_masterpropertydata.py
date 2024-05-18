# Generated by Django 5.0.6 on 2024-05-17 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentscraper', '0013_westwoodlistings_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='MasterPropertyData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('builder_name', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(max_length=500)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('full_url', models.URLField(max_length=500)),
                ('image_urls', models.TextField()),
                ('heat_included', models.BooleanField(default=False)),
                ('hot_water_included', models.BooleanField(default=False)),
                ('cat_allowed', models.BooleanField(default=False)),
                ('dog_allowed', models.BooleanField(default=False)),
                ('balcony', models.BooleanField(default=False)),
                ('in_building_laundry', models.BooleanField(default=False)),
                ('parking_available', models.BooleanField(default=False)),
                ('gym_available', models.BooleanField(default=False)),
                ('price_per_month', models.CharField(max_length=100)),
                ('bedrooms', models.CharField(max_length=50)),
                ('baths', models.FloatField()),
                ('size', models.CharField(max_length=100)),
                ('building_floor_plans', models.TextField(blank=True, null=True)),
                ('hydro_included', models.BooleanField(default=False)),
                ('property_type', models.CharField(max_length=100)),
                ('price_per_sqft', models.CharField(blank=True, max_length=50, null=True)),
                ('listing_address', models.CharField(blank=True, max_length=255, null=True)),
                ('den_included', models.BooleanField(default=False)),
                ('parking', models.CharField(blank=True, max_length=100, null=True)),
                ('number_of_floors', models.IntegerField(blank=True, null=True)),
                ('number_of_units', models.IntegerField(blank=True, null=True)),
                ('year_built', models.IntegerField(blank=True, null=True)),
                ('air_conditioning', models.BooleanField(default=False)),
                ('balcony_patio', models.BooleanField(default=False)),
                ('convenience_store', models.BooleanField(default=False)),
                ('elevator', models.BooleanField(default=False)),
                ('free_outdoor_parking', models.BooleanField(default=False)),
                ('laundry_facilities', models.BooleanField(default=False)),
                ('water_included', models.BooleanField(default=False)),
                ('parking_cost', models.IntegerField(blank=True, null=True)),
                ('parking_type', models.CharField(blank=True, max_length=100, null=True)),
                ('walk_score', models.IntegerField(blank=True, null=True)),
                ('transit_score', models.IntegerField(blank=True, null=True)),
                ('bike_score', models.IntegerField(blank=True, null=True)),
                ('nearest_police_station', models.CharField(blank=True, max_length=255, null=True)),
                ('nearest_superstore', models.CharField(blank=True, max_length=255, null=True)),
                ('nearest_pharmacy', models.CharField(blank=True, max_length=255, null=True)),
                ('nearest_hospital', models.CharField(blank=True, max_length=255, null=True)),
                ('time_to_nearest_hospital', models.CharField(blank=True, max_length=50, null=True)),
                ('time_to_nearest_police_station', models.CharField(blank=True, max_length=50, null=True)),
                ('time_to_nearest_superstore', models.CharField(blank=True, max_length=50, null=True)),
                ('time_to_nearest_pharmacy', models.CharField(blank=True, max_length=50, null=True)),
                ('zone', models.CharField(blank=True, max_length=50, null=True)),
                ('date', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
