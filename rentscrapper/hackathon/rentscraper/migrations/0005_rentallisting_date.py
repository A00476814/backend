# Generated by Django 5.0.6 on 2024-05-16 18:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentscraper', '0004_templetonlisting_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentallisting',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
