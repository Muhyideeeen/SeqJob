from . import models
from utils.process_duration import get_localized_time,converStringToDate,converStringToTime,convertStringToTimeAndAddSomeHours
from django_celery_beat.models import ClockedSchedule, PeriodicTask
import json
from core.celery import app
from celery import shared_task


@shared_task
def create_schedule_interview_time(id):
    instance = models.TrackCandidateInterviewInvitation.objects.get(id=id)
    startdate = converStringToDate(instance.date_picked)
    startTime = converStringToTime(instance.time_picked)

    endTime = convertStringToTimeAndAddSomeHours(instance.time_picked,8)
    # timedelta(hours=3)
    clocked,_ = ClockedSchedule.objects.get_or_create(
    clocked_time=get_localized_time(startdate, startTime, ))
    # this is the time we want to off the interview
    endtimeClocked,_ = ClockedSchedule.objects.get_or_create(
    clocked_time=get_localized_time(startdate, endTime, ))



    PeriodicTask.objects.create(
        clocked=clocked,
        name=f"{str(instance.id)} activate candidate interview",  # task name
        task="interview.tasks.activateInterView",  # task.
        args=json.dumps(
            [
                instance.id,
            ]
        ),  # arguments
        description="this will activate TrackCandidateInterviewInvitation so the user can use the link to attend the interview",
        one_off=True,

    )

    PeriodicTask.objects.create(
        clocked=endtimeClocked,
        name=f"{str(instance.id)} deactivate candidate interview",  # task name
        task="interview.tasks.deactivateInterView",  # task.
        args=json.dumps(
            [
                instance.id,
            ]
        ),  # arguments
        description="this will deactivate TrackCandidateInterviewInvitation so the user can use the link to attend the interview",
        one_off=True,

    )

@app.task()
def activateInterView(track_candidate_interview_invitation_id):
    instance= models.TrackCandidateInterviewInvitation.objects.get(id=track_candidate_interview_invitation_id)
    instance.is_time_for_interview =True 
    instance.save()

    "this si where the code for email and push notification"


@app.task()
def deactivateInterView(track_candidate_interview_invitation_id):
    'we would close this actual interview after on hour or so'
    instance= models.TrackCandidateInterviewInvitation.objects.get(id=track_candidate_interview_invitation_id)
    instance.is_time_for_interview =False 
    instance.save()