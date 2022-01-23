# Generated by Django 3.0.8 on 2022-01-23 12:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Category')),
            ],
            options={
                'ordering': ('course_id',),
            },
        ),
        migrations.AlterModelOptions(
            name='api_key',
            options={'verbose_name': 'API key', 'verbose_name_plural': 'API keys'},
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('level_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=15)),
                ('tagline', models.CharField(max_length=70)),
                ('display_pic', models.ImageField(upload_to='levels')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Course')),
            ],
            options={
                'ordering': ('level_id',),
            },
        ),
    ]
