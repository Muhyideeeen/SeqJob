from rest_framework import viewsets, status
from rest_framework.response import Response
from myauthentication import permissions
from ..serializers import company as company_intervew_serializer
from utils.response_data import response_data
from django.shortcuts import get_object_or_404
from jobs.models import Job,JobApplicant
from utils.exception import CustomValidation
from myauthentication.permissions import JobMustHaveTestOrQuetionSetBeforeInterviewPermissions
from rest_framework.decorators import action
from interview import models as model_interview
from utils.custom_response import Success_response
from interview.serializers import panelist as panelist_serializers
from datetime import datetime
from interview.serializers import job_seekers as seerker_interview_serializer


class CompanySetUpInterView(viewsets.ViewSet):
    permission_classes = [permissions.OnlyCompany,
                          JobMustHaveTestOrQuetionSetBeforeInterviewPermissions]
    serializer_class = company_intervew_serializer.CompanySetUpInterview

    def create(self, request, pk=None):
        job_id = self.request.data.get('job_id', -1)
        job = get_object_or_404(Job, id=job_id)
        self.check_object_permissions(self.request, obj=job)
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = response_data(201, message='Created Job Successfully', data=[])
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        job = get_object_or_404(Job, id=pk)
        try:
            clean_instance = company_intervew_serializer.InterviewCleaner(
                job.interview, many=False)
            data = response_data(201, message='Successfully',
                                data=clean_instance.data)
        except:
            raise CustomValidation(detail='Interview Has Not Been Assigned Yet',field='pk',status_code=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False,)
    def update_interview(self, request, pk=None):
        job_id = self.request.data.get('job_id', -1)
        job = get_object_or_404(Job, id=job_id)
        self.check_object_permissions(self.request, obj=job)
        serializer = self.serializer_class(data=request.data,
                                           instance=model_interview.Interview,
                                           context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        udatedInsterview = serializer.save()
        clean_instance = company_intervew_serializer.InterviewCleaner(
            udatedInsterview, many=False)
        data = response_data(
            200, message='Updated Job Successfully', data=clean_instance.data)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False,)
    def company_update_interview_link(self, request, *args, **kwargs):
        'thisn will update the interview link'
        pk = request.data.get('pk')
        job = get_object_or_404(Job, id=pk)
        new_link = request.data.get('new_link', -1)
        if new_link is None:
            raise CustomValidation(detail='PLease new_link is required')

        interviewID = job.interview.id
        interview = model_interview.Interview.objects.get(id=interviewID)
        interview.interview_link = new_link
        interview.save()
        return Success_response(msg='Success', data=[])

    @action(methods=['get'], detail=False,permission_classes=[permissions.CompanyAndPanelist])
    def get_candidate_that_accepted_interview(self, request, *args, **kwargs):
        'this endpoint accept returns all the cadidates that have picked a date on the interview'
        job_id = request.query_params.get('job_id', None)
        if job_id is None:
            raise CustomValidation('job does not exists', field='error')

        job = get_object_or_404(Job, id=job_id)
        all_intrested_applicant = model_interview.TrackCandidateInterviewInvitation.objects.filter(
            interview=job.interview,
            # if the jobseeker pick this will be true meaning he is actually intresated
            has_picked_invitation=True
        )

        clean_data = company_intervew_serializer.TrackCandidateInterviewInvitationCleaner(
            instance=all_intrested_applicant, many=True)

        return Success_response('Success', data=clean_data.data)


    @action(methods=['get'], detail=False,permission_classes=[permissions.CompanyAndPanelist])
    def get_scheduled_interviews_invite(self,request,*args,**kwargs):
        today = datetime.now().date()   
        
        list_of_invitations = model_interview.TrackCandidateInterviewInvitation.objects.filter(
        date_picked__gte=today,
        has_picked_invitation=True,
        interview__company = request.user.companyprofile
        )

        clean_data = seerker_interview_serializer.InterViewPreviewJobSeekerSerializer(list_of_invitations,many=True)
        # data = response_data(status.HTTP_200_OK,'Succefull',data=clean_data.data)

        return Success_response('Success', clean_data.data) 
