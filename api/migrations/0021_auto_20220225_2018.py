# Generated by Django 3.0.8 on 2022-02-25 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_lastvisited'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LastVisited',
            new_name='LastVisit',
        ),
    ]