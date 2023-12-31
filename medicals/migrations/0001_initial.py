# Generated by Django 4.1.3 on 2023-05-26 05:19

import cloudinary_storage.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0002_initial'),
        ('myauthentication', '0003_alter_user_user_type_medicalrepprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobMedicals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_of_available_dates', models.JSONField()),
                ('list_of_available_time', models.JSONField()),
                ('medical_rep', models.EmailField(max_length=254)),
                ('company', models.ForeignKey(default=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myauthentication.companyprofile')),
                ('job', models.OneToOneField(default=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
                ('selected_job_seekers', models.ManyToManyField(to='myauthentication.jobseekerprofile')),
            ],
        ),
        migrations.CreateModel(
            name='TrackCandidateJobMedicalsInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_picked', models.DateField(default=None, null=True)),
                ('time_picked', models.TimeField(default=None, null=True)),
                ('has_mail_sent', models.BooleanField(default=False)),
                ('has_picked_invitation', models.BooleanField(default=False)),
                ('job_medicals', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicals.jobmedicals')),
                ('job_seeker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myauthentication.jobseekerprofile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedMedicalReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('candidates', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicals.trackcandidatejobmedicalsinvitation')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedMedicalReportFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('files', models.FileField(default=None, null=True, storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(), upload_to='medical_uploaded_report')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicals.uploadedmedicalreport')),
            ],
        ),
    ]
