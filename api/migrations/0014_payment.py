# Generated by Django 3.0.8 on 2022-01-28 13:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20220128_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('pay_id', models.AutoField(primary_key=True, serialize=False)),
                ('ephemeral_key', models.CharField(max_length=60)),
                ('payment_intent', models.CharField(max_length=60)),
                ('status', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Subscription')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.SystemUser')),
            ],
        ),
    ]
