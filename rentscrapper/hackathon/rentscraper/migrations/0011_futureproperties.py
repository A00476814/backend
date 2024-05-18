# Generated by Django 5.0.6 on 2024-05-17 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentscraper', '0010_alter_westwoodlistings_bedrooms'),
    ]

    operations = [
        migrations.CreateModel(
            name='FutureProperties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('date_of_post', models.CharField(max_length=100)),
                ('blog_link', models.URLField()),
                ('image_url', models.URLField()),
                ('floors', models.CharField(max_length=50)),
                ('units', models.CharField(max_length=50)),
                ('cost', models.CharField(max_length=50)),
                ('property_type', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=255)),
                ('builder', models.CharField(max_length=255)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('zone', models.CharField(max_length=100)),
            ],
        ),
    ]
