# Generated by Django 5.0.3 on 2024-07-17 06:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_portal', '0004_alter_mail_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 7, 17, 6, 31, 16, 156736)),
        ),
    ]