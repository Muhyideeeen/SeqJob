from django.db import models
from myauthentication import models as auth_models
from jobs import models as job_models


class Interview(models.Model):
    company = models.ForeignKey(auth_models.CompanyProfile,null=True,default=True,on_delete=models.CASCADE,)
    job = models.OneToOneField(job_models.Job,null=True,default=True,on_delete=models.CASCADE,)
    list_of_available_dates = models.JSONField()
    list_of_available_time = models.JSONField()
    # rating sheet is a list of dictinary e.g [{'Qualification':20,'Knowledge':'20}:]
    rating_sheet = models.JSONField()
    # list of panelist emails
    list_of_email = models.JSONField()
    interview_link = models.TextField(default=' ')
    panelist_invitation_letter = models.TextField(default='N/A') 

class TrackCandidateInterviewInvitation(models.Model):
    job_seeker =models.ForeignKey(auth_models.JobSeekerProfile,on_delete=models.CASCADE)
    interview = models.ForeignKey(Interview,on_delete=models.CASCADE)
    date_picked = models.DateField(null=True,default=None)
    time_picked = models.TimeField(null=True,default=None,)
    has_mail_sent = models.BooleanField(default=False)
    has_picked_invitation = models.BooleanField(default=False)
    is_time_for_interview = models.BooleanField(default=False)

    
class CandidateInterviewSheet(models.Model):
    interview = models.ForeignKey(Interview,on_delete=models.CASCADE)
    job_seeker =models.ForeignKey(auth_models.JobSeekerProfile,on_delete=models.CASCADE)
    panelist = models.ForeignKey(auth_models.PanelistProfile,null=True,on_delete=models.SET_NULL)

    # contains list of {value:'',score:21,cut_off:2}
    rating_sheet = models.JSONField(null=True,default=None)
    interviewer_remark  = models.TextField(default='.')
    summary_of_qualification  = models.TextField(default='.')