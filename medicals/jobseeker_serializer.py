from rest_framework import serializers
from . import models
from utils.exception import CustomValidation
from django.shortcuts import get_object_or_404
import json
from jobs.serializers import job_seekers as job_seekers_serialzier


class JobMedicalsPreviewJobSeekerSerializer(serializers.ModelSerializer):
    job_medicals = serializers.SerializerMethodField()

    def get_job_medicals(self,instance: models.TrackCandidateJobMedicalsInvitation):

        return{
            'job_title': instance.job_medicals.job.job_title,
            'job_medicals_id':instance.job_medicals.id,
            'company':instance.job_medicals.company.organisation_name
        }

    class Meta:
        model = models.TrackCandidateJobMedicalsInvitation
        fields = ['job_seeker','job_medicals','id','date_picked','time_picked']



class JobSeekerScheduleJobMedicalsDate(serializers.Serializer):
    available_time =serializers.TimeField()
    available_dates =serializers.DateField()
    medicals_id = serializers.IntegerField()

    def create(self, validated_data):
        '''
            the job seeker picks a date he would love to be medical echeck
        '''
        medicals_id  = validated_data.get('medicals_id')
        available_time  = validated_data.get('available_time')
        available_dates  = validated_data.get('available_dates')
        job_medicals = get_object_or_404(models.JobMedicals,id=medicals_id)
        job_seeker =self.context.get('request').user.jobseekerprofile



        "we need to get all the available dates and set is_pick so another person cant pick"
        list_of_available_dates = json.loads(job_medicals.list_of_available_dates)
        list_of_available_time = json.loads(job_medicals.list_of_available_time)

        if models.TrackCandidateJobMedicalsInvitation.objects.filter(job_medicals =job_medicals,
            date_picked=available_dates,time_picked=available_time
        ).exists():
            raise CustomValidation(detail='This That has Been Selected Already',field='error')



        if models.TrackCandidateJobMedicalsInvitation.objects.filter(job_medicals =job_medicals,job_seeker=job_seeker,has_picked_invitation=True
        ).exists():
            raise CustomValidation(detail='You Have Scheduled already',field='error')
        

        for time in list_of_available_time:
            if time.get('available_time') == str(available_time):
                time['is_selected'] = True
        for date in list_of_available_dates:
            if date.get('available_dates') ==str(available_dates):
                date['is_selected'] = True

        job_medicals.list_of_available_time = json.dumps(list_of_available_time)
        job_medicals.list_of_available_dates = json.dumps(list_of_available_dates)
        job_medicals.save()
        job_medicals_invitation = models.TrackCandidateJobMedicalsInvitation.objects.filter(
            job_seeker=job_seeker,
            job_medicals=job_medicals,
        ).first()
        job_medicals_invitation.date_picked = available_dates
        job_medicals_invitation.time_picked = available_time
        job_medicals_invitation.has_picked_invitation=True
        job_medicals_invitation.save()




        return  job_medicals



class JobMedicalsCleanerJobSeekerSerializer(serializers.ModelSerializer):
    job_medicals = serializers.SerializerMethodField()


    def get_job_medicals(self,instance: models.TrackCandidateJobMedicalsInvitation):
        job=None
        try:
            job = instance.job_medicals.job
            cleaned_job = job_seekers_serialzier.JobCleanerForJobSeekerSerializer(instance=job,many=False)
            job_medicals_link = 'pending'
            if instance.is_time_for_interview:
                job_medicals_link = instance.job_medicals.interview_link
            return   {
                'job':cleaned_job.data,
                'medicals_id':instance.job_medicals.id,
                'dates_related_data':{
                    'dates':json.loads(instance.job_medicals.list_of_available_dates),
                    'times':json.loads(instance.job_medicals.list_of_available_time),
                },
                'interview_link':job_medicals_link,
                'is_time_for_interview':instance.is_time_for_interview,
                'has_picked_invitation':instance.has_picked_invitation
            }
        except:
            return False
        # return instance

    class Meta:
        model  = models.TrackCandidateJobMedicalsInvitation
        fields = [ 'job_seeker', 'job_medicals','date_picked','time_picked',]

