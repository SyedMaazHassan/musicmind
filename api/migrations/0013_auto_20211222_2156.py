# Generated by Django 3.0.8 on 2021-12-22 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_apitoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemuser',
            name='uid',
            field=models.CharField(default=None, max_length=255, unique=True),
        ),
    ]
