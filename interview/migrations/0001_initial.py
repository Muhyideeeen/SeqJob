# Generated by Django 4.1.3 on 2023-05-06 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateInterviewSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_sheet', models.JSONField(default=None, null=True)),
                ('interviewer_remark', models.TextField(default='.')),
                ('summary_of_qualification', models.TextField(default='.')),
            ],
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_of_available_dates', models.JSONField()),
                ('list_of_available_time', models.JSONField()),
                ('rating_sheet', models.JSONField()),
                ('list_of_email', models.JSONField()),
                ('interview_link', models.TextField(default=' ')),
            ],
        ),
        migrations.CreateModel(
            name='TrackCandidateInterviewInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_picked', models.DateField(default=None, null=True)),
                ('time_picked', models.TimeField(default=None, null=True)),
                ('has_mail_sent', models.BooleanField(default=False)),
                ('has_picked_invitation', models.BooleanField(default=False)),
                ('is_time_for_interview', models.BooleanField(default=False)),
                ('interview', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interview.interview')),
            ],
        ),
    ]