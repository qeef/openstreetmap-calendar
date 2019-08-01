# Generated by Django 2.2.3 on 2019-08-01 08:00

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0007_event_location_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='location_text',
        ),
        migrations.AddField(
            model_name='event',
            name='location_address',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]