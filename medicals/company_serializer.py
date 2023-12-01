from rest_framework import serializers
from . import models
from jobs.models import Job,JobApplicant
from django.shortcuts import get_object_or_404
from utils.exception import CustomValidation
from myauthentication import models as auth_models
import json
from medicals.task import handle_invite_job_seeker_for_medic

class ListOfAvailableDates(serializers.Serializer):
    available_dates =serializers.DateField()


class ListOfAvailableTime(serializers.Serializer):
    available_time =serializers.TimeField()

class SelectedCandidates(serializers.Serializer):
    id = serializers.IntegerField()
class CompanySetUpMedicals(serializers.Serializer):
    job_id = serializers.IntegerField()
    list_of_available_dates =ListOfAvailableDates(many=True)
    list_of_available_time = ListOfAvailableTime(many=True)
    medical_rep = serializers.EmailField()
    selected_candidates = SelectedCandidates(many=True)


    def _validate_job_is_for_company(self,attrs):
        job:Job  = get_object_or_404(Job,id=attrs.get('job_id',-1))
        medical_rep = attrs.get('medical_rep')
        check_if_job_has_medic=False
        try:
            job.jobmedicals
            check_if_job_has_medic=True
        except:
            check_if_job_has_medic=False
        if  check_if_job_has_medic:
            raise CustomValidation('Already has Medicals',field='job_id')

 
        errors= []

        current_user =auth_models.User.objects.filter(email=medical_rep)
        if current_user.exists():
            current_user = current_user.first()
            if current_user.user_type == 'medic':
                pass 
            else:
                errors.append(f'{medical_rep} already exists as a {current_user.user_type}')

        if len(errors) !=0:
            raise CustomValidation(errors,field='list_of_email')


    def create(self, validated_data):
        self._validate_job_is_for_company(validated_data)
        job_id = validated_data.get('job_id')
        list_of_available_dates =validated_data.get('list_of_available_dates')
        list_of_available_time = validated_data.get('list_of_available_time')
        medical_rep =validated_data.get('medical_rep')
        selected_candidates = validated_data.get('selected_candidates',[])
        job:Job  = get_object_or_404(Job,id=job_id)

        medic = models.JobMedicals.objects.create(
            company = self.context.get('request').user.companyprofile,
            job = job,
            list_of_available_dates=json.dumps(list_of_available_dates,default=str),
            list_of_available_time=json.dumps(list_of_available_time,default=str),
            medical_rep =medical_rep,
        )
        for eachCadidate in selected_candidates:
            user=auth_models.User.objects.filter(id=eachCadidate.get('id')).first()
            if user:
                if user.user_type == 'job_seakers':
                    medic.selected_job_seekers.add(user.jobseekerprofile)
                    medic.save()
        handle_invite_job_seeker_for_medic.delay(medic.id)
        return medic