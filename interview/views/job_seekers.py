from rest_framework import viewsets,status
from interview.serializers.job_seekers import InterViewCleanerJobSeekerSerializer,InterViewPreviewJobSeekerSerializer,JobSeekerScheduleInterviewDateSerializer
from myauthentication.permissions import MustHaveCV,OnlyJobSeeker
from .. import models
from rest_framework.response import Response
from utils.response_data import response_data
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db.models import Q as qObjects
from datetime import datetime, timedelta, time

class JobSeekersManageInterviewViewSet(viewsets.ViewSet):
    permission_classes = [OnlyJobSeeker,MustHaveCV]
    serializer_class = InterViewPreviewJobSeekerSerializer
    def list(self,request,*args,**kwargs):
        filter_by_scheduled  = request.query_params.get('filter_by_scheduled','unscheduled')
        today = datetime.now().date()   
        list_of_invitations =  None
        if filter_by_scheduled=='unscheduled':
            list_of_invitations = models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=request.user.jobseekerprofile,
            # date_picked__gte=today,
                has_picked_invitation=False
            )
        else:
            list_of_invitations = models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=request.user.jobseekerprofile,
            date_picked__gte=today,
            has_picked_invitation=True
            )

        clean_data = self.serializer_class(list_of_invitations,many=True)
        data = response_data(status.HTTP_200_OK,'Succefull',data=clean_data.data)

        return Response(data,status=status.HTTP_200_OK) 
    

    def retrieve(self,request,pk=None):
        invitaion = get_object_or_404( models.TrackCandidateInterviewInvitation,id=pk)
        serializer_class =InterViewCleanerJobSeekerSerializer

        clean_data = serializer_class(invitaion,many=False)

        data = response_data(status.HTTP_200_OK,'Succefull',data=clean_data.data)

        return Response(data,status=status.HTTP_200_OK) 

    @action(methods=['post'],detail=False)
    def pick_date(self,request,*args,**Kwargs):
        serializer_class = JobSeekerScheduleInterviewDateSerializer(data=request.data,context={'request':request}) 

        serializer_class.is_valid(raise_exception=True)
        serializer_class.save()

        data = response_data(status.HTTP_200_OK,'Succefull',data=[])

        return Response(data,status=status.HTTP_200_OK) 

