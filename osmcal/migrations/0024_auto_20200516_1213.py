# Generated by Django 3.0.6 on 2020-05-16 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0023_user_primary_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='osm_id',
            field=models.IntegerField(null=True),
        ),
    ]
