from django.db import models
from myauthentication import models as auth_models
from jobs import models as job_models
from cloudinary_storage.storage import RawMediaCloudinaryStorage



class JobMedicals(models.Model):
    company = models.ForeignKey(auth_models.CompanyProfile,null=True,default=True,on_delete=models.CASCADE,)
    job = models.OneToOneField(job_models.Job,null=True,default=True,on_delete=models.CASCADE,)
    list_of_available_dates = models.JSONField()
    list_of_available_time = models.JSONField()

    medical_rep = models.EmailField()
    selected_job_seekers = models.ManyToManyField(auth_models.JobSeekerProfile)

class TrackCandidateJobMedicalsInvitation(models.Model):
    job_seeker =models.ForeignKey(auth_models.JobSeekerProfile,on_delete=models.CASCADE)
    job_medicals = models.ForeignKey(JobMedicals,on_delete=models.CASCADE)
    date_picked = models.DateField(null=True,default=None)
    time_picked = models.TimeField(null=True,default=None,)
    has_mail_sent = models.BooleanField(default=False)
    has_picked_invitation = models.BooleanField(default=False)
    is_time_for_interview = models.BooleanField(default=False)
    interview_link = models.TextField(default='',null=True,blank=True)


class UploadedMedicalReport(models.Model):
    candidates = models.ForeignKey(TrackCandidateJobMedicalsInvitation,on_delete=models.CASCADE)


class UploadedMedicalReportFiles(models.Model):
    report = models.ForeignKey(UploadedMedicalReport,on_delete=models.CASCADE)
    files =models.FileField(upload_to='medical_uploaded_report',null=True,default=None,
        storage=RawMediaCloudinaryStorage(),)