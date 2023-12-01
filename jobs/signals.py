from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from mailing.tasks import handle_send_application_letters
from myauthentication.models import JobSeekerProfile
from .tasks import send_new_jobs_reminder_to_intrested_seekers
from utils.notification import NovuProvider


@receiver(post_save,sender=models.Job)
def job_reminder_signal(sender,**kwargs):
    'this are all job seekers that are registered job notification function'
    # if kwargs['created']:
    job = kwargs['instance']
    if job.is_active== True:
        user_ids=list(map(lambda seeker:seeker.user.id, JobSeekerProfile.objects.all()))
        novu = NovuProvider()
        novu.send_notification(
        name='sequential-jobs-api',
        sub_id=user_ids,
        title=f'Apply for {job.job_title}',
        content='a new job has been create please apply')
        send_new_jobs_reminder_to_intrested_seekers.delay(job.id)

@receiver(post_save,sender=models.JobApplicant)
def handle_sending_letters(sender,**kwargs):
    "once the jobApplicant is updated it sends a signal here to proccess sending letters"

    job_applicant  = kwargs['instance']

    if job_applicant.has_sent_selection_mail== False:
        if job_applicant.final_selection_state!='idle':
            handle_send_application_letters.delay(
                job_applicant.jobseekers.user.id,job_applicant.id,
            job_applicant.job.job_title)