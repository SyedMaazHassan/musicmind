# Generated by Django 3.0.8 on 2022-01-28 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trial',
            old_name='id',
            new_name='trial_id',
        ),
    ]