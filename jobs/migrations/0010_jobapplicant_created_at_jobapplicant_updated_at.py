# Generated by Django 4.1.3 on 2023-07-14 15:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_alter_jobtestquetion_suitable'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplicant',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jobapplicant',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
