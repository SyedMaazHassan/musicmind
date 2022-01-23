# Generated by Django 3.0.8 on 2022-01-23 16:26

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_delete_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('video_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=15)),
                ('description', models.CharField(max_length=50)),
                ('video_url', models.FileField(upload_to='videos')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('mission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='video', to='api.Mission')),
            ],
            options={
                'ordering': ('video_id',),
            },
        ),
    ]
