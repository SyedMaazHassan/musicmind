# Generated by Django 3.0.8 on 2022-01-22 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20220122_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemuser',
            name='phone',
            field=models.IntegerField(),
        ),
    ]
