# Generated by Django 4.1.3 on 2023-05-27 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackcandidatejobmedicalsinvitation',
            name='interview_link',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='trackcandidatejobmedicalsinvitation',
            name='is_time_for_interview',
            field=models.BooleanField(default=False),
        ),
    ]
