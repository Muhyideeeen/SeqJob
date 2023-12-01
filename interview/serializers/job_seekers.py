from rest_framework import serializers
from .. import models
from jobs.serializers import job_seekers as job_seekers_serialzier
from utils.exception import CustomValidation
from django.shortcuts import get_object_or_404
import json
from interview.tasks import create_schedule_interview_time
class InterViewCleanerJobSeekerSerializer(serializers.ModelSerializer):
    interview = serializers.SerializerMethodField()


    def get_interview(self,instance: models.TrackCandidateInterviewInvitation):
        job=None
        try:
            job = instance.interview.job
            cleaned_job = job_seekers_serialzier.JobCleanerForJobSeekerSerializer(instance=job,many=False)
            interview_link = 'pending'
            if instance.is_time_for_interview:
                interview_link = instance.interview.interview_link
            return   {
                'job':cleaned_job.data,
                'interview_id':instance.interview.id,
                'dates_related_data':{
                    'dates':json.loads(instance.interview.list_of_available_dates),
                    'times':json.loads(instance.interview.list_of_available_time),
                },
                'interview_link':interview_link,
                'is_time_for_interview':instance.is_time_for_interview,
                'has_picked_invitation':instance.has_picked_invitation
            }
        except:
            return False
        return 

    class Meta:
        model  = models.TrackCandidateInterviewInvitation
        fields = [ 'job_seeker', 'interview','date_picked','time_picked',]

class InterViewPreviewJobSeekerSerializer(serializers.ModelSerializer):
    interview = serializers.SerializerMethodField()

    def get_interview(self,instance: models.TrackCandidateInterviewInvitation):

        return{
            'job_title': instance.interview.job.job_title,
            'interview_id':instance.interview.id,
            'company':instance.interview.company.organisation_name
        }

    class Meta:
        model = models.TrackCandidateInterviewInvitation
        fields = ['job_seeker','interview','id','date_picked','time_picked']


class JobSeekerScheduleInterviewDateSerializer(serializers.Serializer):
    available_time =serializers.TimeField()
    available_dates =serializers.DateField()
    interview_id = serializers.IntegerField()

    def create(self, validated_data):
        '''
            the job seeker picks a date he would love to be interviewed
        '''
        interview_id  = validated_data.get('interview_id')
        available_time  = validated_data.get('available_time')
        available_dates  = validated_data.get('available_dates')
        interview = get_object_or_404(models.Interview,id=interview_id)
        job_seeker =self.context.get('request').user.jobseekerprofile


        "we need to get all the available dates and set is_pick so another person cant pick"
        list_of_available_dates = json.loads(interview.list_of_available_dates)
        list_of_available_time = json.loads(interview.list_of_available_time)

        print("Hello world")
        if models.TrackCandidateInterviewInvitation.objects.filter(interview =interview,
            date_picked=available_dates,time_picked=available_time
        ).exists():
            raise CustomValidation(detail='This That has Been Selected Already',field='error')

        if models.TrackCandidateInterviewInvitation.objects.filter(interview =interview,job_seeker=job_seeker,has_picked_invitation=True
        ).exists():
            raise CustomValidation(detail='You Have Scheduled already',field='error')
        for time in list_of_available_time:
            if time.get('available_time') == str(available_time):
                time['is_selected'] = True
        for date in list_of_available_dates:
            if date.get('available_dates') ==str(available_dates):
                date['is_selected'] = True


        
        interview.list_of_available_time = json.dumps(list_of_available_time)
        interview.list_of_available_dates = json.dumps(list_of_available_dates)
        interview.save()
        interview_invitation = models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=job_seeker,
            interview=interview,
        ).first()
        interview_invitation.date_picked = available_dates
        interview_invitation.time_picked = available_time
        interview_invitation.has_picked_invitation=True
        interview_invitation.save()

        create_schedule_interview_time.delay(interview_invitation.id)

        return interview
