# Generated by Django 5.0.6 on 2024-05-16 18:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentscraper', '0003_templetonlisting'),
    ]

    operations = [
        migrations.AddField(
            model_name='templetonlisting',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
