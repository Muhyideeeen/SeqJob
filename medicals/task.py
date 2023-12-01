from time import sleep
from mailing.EmailConfirmation import activateEmail,activatePanelistEmail,invitePanelist,invite_job_seeker,send_application_letters
from celery import shared_task
from django.contrib.auth import get_user_model
from jobs import models as job_models
from mailing.EmailConfirmation import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
import os,json
from . import models
from utils.process_duration import get_localized_time,converStringToDate,converStringToTime,convertStringToTimeAndAddSomeHours
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from core.celery import app


@shared_task
def create_schedule_medical_time(id):
    instance = models.TrackCandidateJobMedicalsInvitation.objects.get(id=id)

    startdate = converStringToDate(instance.date_picked)
    startTime = converStringToTime(instance.time_picked)

    endTime = convertStringToTimeAndAddSomeHours(instance.time_picked,8)
    clocked,_ = ClockedSchedule.objects.get_or_create(
    clocked_time=get_localized_time(startdate, startTime, ))
    # this is the time we want to off the interview
    endtimeClocked,_ = ClockedSchedule.objects.get_or_create(
    clocked_time=get_localized_time(startdate, endTime, ))

    PeriodicTask.objects.create(
        clocked=clocked,
        name=f"{str(instance.id)} activate candidate medicals",  # task name
        task="medicals.tasks.activateMedicals",  # task.
        args=json.dumps(
            [
                instance.id,
            ]
        ),  # arguments
        description="this will activate TrackCandidateJobMedicalsInvitation so the user can use the link to attend the interview",
        one_off=True,

    )
    PeriodicTask.objects.create(
        clocked=endtimeClocked,
        name=f"{str(instance.id)} deactivate candidate medical",  # task name
        task="interview.tasks.deactivateMedicals",  # task.
        args=json.dumps(
            [
                instance.id,
            ]
        ),  # arguments
        description="this will deactivate TrackCandidateJobMedicalsInvitation so the user can use the link to attend the interview",
        one_off=True,
    )




@app.task()
def activateInterView(track_candidate_jobmedical_invitation_id):
    instance= models.TrackCandidateJobMedicalsInvitation.objects.get(id=track_candidate_jobmedical_invitation_id)
    instance.is_time_for_interview =True 
    instance.save()

    "this si where the code for email and push notification"


@app.task()
def deactivateInterView(track_candidate_jobmedical_invitation_id):
    'we would close this actual medicals after on hour or so'
    instance= models.TrackCandidateJobMedicalsInvitation.objects.get(id=track_candidate_jobmedical_invitation_id)
    instance.is_time_for_interview =False 
    instance.save()


@shared_task()
def handle_invite_job_seeker_for_medic(JobMedicalsID,):
    jobmedicals = models.JobMedicals.objects.get(id=JobMedicalsID)
    for JobSeekerProfile in jobmedicals.selected_job_seekers.all():
        job_applicant = job_models.JobApplicant.objects.filter(jobseekers__id=JobSeekerProfile.id,job__id=jobmedicals.job.id).first()
        print({
            'JobSeekerProfile':JobSeekerProfile,
            'job_applicant':job_applicant,
            'jobID':jobmedicals.job.id
        })
        if job_applicant:
            if job_applicant.has_been_invited_for_medicals== False:
                job_applicant.has_been_invited_for_medicals=True
                job_applicant.save()
                invitation =models.TrackCandidateJobMedicalsInvitation.objects.create(
                    job_seeker = job_applicant.jobseekers,
                    job_medicals= jobmedicals,
                    has_mail_sent=True
                )
                invitation.save()
                to_email = job_applicant.jobseekers.user.email
                companyName = jobmedicals.company.organisation_name
                mail_subject = f'{companyName} Has Invited For an Interview on Sequntial Job APP'
                data = {
                        'user':job_applicant.jobseekers.user,
                        'domain':os.environ['domain'],
                        'companyName':companyName

                }
                message = render_to_string('job_seeker_invite_from_medic.html',context=data)

                send_mail(
                    subject=mail_subject,
                    html_content=message,
                    sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
                    to=[{"email":to_email,"name":"rel8"}])