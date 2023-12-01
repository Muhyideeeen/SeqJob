
from rest_framework import viewsets,status
from rest_framework.response import Response
from myauthentication import permissions
from utils.response_data import response_data
from django.shortcuts import get_object_or_404
from jobs.models import Job 
from .. import models
from datetime import datetime, timedelta, time
from .. import jobseeker_serializer
from rest_framework.decorators import action
from utils.custom_response import Success_response

class JobSeekerManageMedicals(viewsets.ViewSet):
    serializer_class = jobseeker_serializer.JobMedicalsPreviewJobSeekerSerializer
    permission_classes = [permissions.OnlyJobSeeker,]

    def retrieve(self,request,pk=None):
        invitaion = get_object_or_404( models.TrackCandidateJobMedicalsInvitation,id=pk)
        serializer_class =jobseeker_serializer.JobMedicalsCleanerJobSeekerSerializer

        clean_data = serializer_class(invitaion,many=False)

        data = response_data(status.HTTP_200_OK,'Succefull',data=clean_data.data)

        return Response(data,status=status.HTTP_200_OK) 

    @action(methods=['get'],detail=False)
    def get_medicals_invitation(self,request,*args,**kwargs):
        'see the list of medicals invitaion for medical Note the job seeker has picked a date yet'
        today = datetime.now().date()
        filter_by_scheduled  = request.query_params.get('filter_by_scheduled','unscheduled')
        list_of_invitations =  None
        if filter_by_scheduled=='unscheduled':
            instance = models.TrackCandidateJobMedicalsInvitation.objects.filter(
                job_seeker=request.user.jobseekerprofile,
                has_picked_invitation=False,
            )
        else:
            instance = models.TrackCandidateJobMedicalsInvitation.objects.filter(
            job_seeker=request.user.jobseekerprofile,
            has_picked_invitation=True,
             date_picked__gte=today,
            )
        serializer = self.serializer_class(instance=instance,many=True)
        

        return Success_response('Success',data=serializer.data,)    


    @action(methods=['post'],detail=False)
    def pick_date(self,request,*args,**kwargs):
        serializer_class = jobseeker_serializer.JobSeekerScheduleJobMedicalsDate(data=request.data,context={'request':request}) 

        serializer_class.is_valid(raise_exception=True)
        serializer_class.save()

        data = response_data(status.HTTP_200_OK,'Succefull',data=[])

        return Response(data,status=status.HTTP_200_OK) 
