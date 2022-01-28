# Generated by Django 3.0.8 on 2022-01-28 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_remove_systemuser_stripe_cust_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemuser',
            name='stripe_cust_id',
            field=models.CharField(blank=True, default=None, max_length=25, null=True),
        ),
    ]