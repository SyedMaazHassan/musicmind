# Generated by Django 3.0.8 on 2022-02-25 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20220225_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lastvisit',
            name='mission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Mission'),
        ),
    ]
