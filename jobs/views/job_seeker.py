from rest_framework import viewsets,status,permissions
from interview.serializers.company import TrackCandidateInterviewInvitationCleaner
from myauthentication.models import JobSeekerProfile
from myauthentication.permissions import MustHaveCV,OnlyJobSeeker
from jobs.serializers import job_seekers as job_seekers_serializer
from jobs.models import Job,JobApplicant
from rest_framework.response import Response
from utils.response_data import response_data
from rest_framework.decorators import action,permission_classes as permission_classes_decorator
from django.shortcuts import get_object_or_404
from utils.exception import CustomValidation
from jobs.serializers import general as general_job_serializer
from rest_framework.viewsets import GenericViewSet,mixins
from utils.custom_response import Success_response
from jobs import filter as custom_filter
from interview import models as interview_related_models
from datetime import datetime, timedelta, time
from utils.notification import NovuProvider

class JobSeekerDashboard(viewsets.ViewSet):
    permission_classes = [OnlyJobSeeker,MustHaveCV]
    filterset_class = custom_filter.JobFIlter

    @action(methods=['get'],detail=False,permission_classes=[])
    def dashboard_summary(self,request,*args,**kwargs):
        today = datetime.now().date()
        job_seeker = request.user.jobseekerprofile
        jobs_applied_for = JobApplicant.objects.filter(
            jobseekers=job_seeker).count()
        interviews_attended = interview_related_models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=job_seeker,is_time_for_interview=True,
            has_picked_invitation=True
        ).count()

        jobs_test_taken = JobApplicant.objects.filter(
            jobseekers=job_seeker,has_written_test=True,job__job_variant='filter_and_test').count()
        jobs_test_scheduled = JobApplicant.objects.filter(
             jobseekers=job_seeker,has_written_test=False,job__job_variant='filter_and_test').count()
 
        interview_scheduled =interview_related_models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=job_seeker,
            # ,is_time_for_interview=False
            date_picked__gte=today,
            has_picked_invitation=True
        ).count()

        job_offers = JobApplicant.objects.filter(
        jobseekers=job_seeker,final_selection_state='selected').count()


        return Success_response('Success',data={
          'jobs_applied_for':jobs_applied_for,  
          'interviews_attended':interviews_attended,  
          'jobs_test_taken':jobs_test_taken,  
          'jobs_test_scheduled':jobs_test_scheduled,  
          'interview_scheduled':interview_scheduled,  
          'job_offers':job_offers,  
        })

    @action(methods=['get'],detail=False,permission_classes=[])
    def jobs_applied_for(self,request,*args,**kwargs):
        job_seeker = request.user.jobseekerprofile
        
        jobs_applied_for = JobApplicant.objects.filter(
        jobseekers=job_seeker)
        clean_data = job_seekers_serializer.JobsAppliedForCleaner(instance=jobs_applied_for,many=True)

        return Success_response('success',data=clean_data.data)

    @action(methods=['get'],detail=False,permission_classes=[])
    def interview_scheduled(self,request,*args,**kwargs):
        job_seeker = request.user.jobseekerprofile
        today = datetime.now().date()
        
        interview_scheduled =interview_related_models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=job_seeker,
            # ,is_time_for_interview=False
            date_picked__lte=today,
            has_picked_invitation=True
        )   
        clean_data =TrackCandidateInterviewInvitationCleaner(instance=interview_scheduled,many=True)
        return Success_response('success',data=clean_data.data)


    @action(methods=['get'],detail=False,permission_classes=[])
    def interviews_attended(self,request,*args,**kwargs):
        job_seeker = request.user.jobseekerprofile
        today = datetime.now().date()
        
        instance = interview_related_models.TrackCandidateInterviewInvitation.objects.filter(
            job_seeker=job_seeker,is_time_for_interview=True,
            has_picked_invitation=True

        )
        clean_data =TrackCandidateInterviewInvitationCleaner(instance=instance,many=True)
        return Success_response('success',data=clean_data.data)


 
   
   
    @action(methods=['get'],detail=False,permission_classes=[])
    def jobs_test_scheduled(self,request,*args,**kwargs):
        job_seeker = request.user.jobseekerprofile
        instance = JobApplicant.objects.filter(
             jobseekers=job_seeker,has_written_test=False,job__job_variant='filter_and_test')
 
        clean_data = job_seekers_serializer.JobsAppliedForCleaner(instance=instance,many=True)

        return Success_response('success',data=clean_data.data)


    @action(methods=['get'],detail=False,permission_classes=[])
    def jobs_test_taken(self,request,*args,**kwargs):
        job_seeker = request.user.jobseekerprofile
        instance = JobApplicant.objects.filter(
            jobseekers=job_seeker,has_written_test=True,job__job_variant='filter_and_test')

        clean_data = job_seekers_serializer.JobsAppliedForCleaner(instance=instance,many=True)

        return Success_response('success',data=clean_data.data)

class JobSeekersApply(viewsets.ViewSet):
    permission_classes = [OnlyJobSeeker,MustHaveCV]
    serializer_class = job_seekers_serializer.ApplyForJobSerializer
    filterset_class = custom_filter.JobFIlter


    def retrieve(self, request, *args, **kwargs):
        print({'kwargs':kwargs})
        instance = get_object_or_404(Job,id=kwargs.get('pk',-1))
        serializer = job_seekers_serializer.JobCleanerForJobSeekerSerializer(instance,many=False)
        data = response_data(status.HTTP_200_OK,' Succefful',data=serializer.data)

        return Response(data,status=status.HTTP_200_OK) 


    def list(self,request,*args,**kwargs):
        all_jobs = Job.objects.all().filter(is_active=True)
        filter_set = self.filterset_class(request.query_params,queryset=all_jobs)
        serialize = job_seekers_serializer.JobCleanerForJobSeekerSerializer(instance=filter_set.qs,many=True)
        data = response_data(status.HTTP_200_OK,' Succefful',data=serialize.data)

        return Response(data,status=status.HTTP_200_OK) 

    @permission_classes_decorator([permissions.AllowAny])
    @action(methods=['get'],detail=False,permission_classes=[])
    def unauth_get_job_route(self,request,*args,**kwargs):
        all_jobs = Job.objects.all().filter(is_active=True)
        filter_set = self.filterset_class(request.query_params,queryset=all_jobs)
        serialize = job_seekers_serializer.JobCleanerForJobSeekerSerializer(instance=filter_set.qs,many=True)
        data = response_data(status.HTTP_200_OK,' Succefful',data=serialize.data)

        return Response(data,status=status.HTTP_200_OK) 
    def create(self,request,format=None):
        # endpoint to apply for a job 
        #cant apply twice 
        serialize = self.serializer_class(data=request.data,context={'request':request})
        serialize.is_valid(raise_exception=True)
        serialize.save()
        data = response_data(status.HTTP_201_CREATED,'Application Succefful',data=[])

        return Response(data,status=status.HTTP_201_CREATED) 

    @action(methods=['post'],detail=False)
    def get_quetion(self,request,format=None):
        # endpoint to get job exam 
        job_id = request.data.get('job_id',-1)
        job = get_object_or_404(Job,id=job_id)

        applicant = get_object_or_404(JobApplicant,job=job,jobseekers=request.user.jobseekerprofile)
        if applicant.has_written_exam==True:
            raise CustomValidation(detail='sorry you have written this exam',field='job_id',)


        clean_data = general_job_serializer.FilterQuetionFormatterSerializer(instance=job.job_filter,many=False)

        data = response_data(status=200,message='success',data=clean_data.data)
        return Response(data,status=status.HTTP_200_OK)





    @action(methods=['post'],detail=False)
    def submit_quetion(self,request,format=None):
        serializer = job_seekers_serializer.HandleQuetionMarkingSerializer(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        data = response_data(status.HTTP_201_CREATED,'Submmited',[result])
        return Response(data,status=status.HTTP_201_CREATED)

    @action(methods=['post'],detail=False)
    def submit_test(self,request,format=None):
        serializer = job_seekers_serializer.HandleTestMarkingSerializer(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        data = response_data(status.HTTP_201_CREATED,'Submmited',[result])
        return Response(data,status=status.HTTP_201_CREATED)



    @action(methods=['post'],detail=False)
    def get_test(self,request,format=None):
        # endpoint to get job exam 
        job_id = request.data.get('job_id',-1)
        job = get_object_or_404(Job,id=job_id)
        if job.job_test is None: raise CustomValidation(detail='Job test does not exist for this job',field='error')
        applicant = get_object_or_404(JobApplicant,job=job,jobseekers=request.user.jobseekerprofile)
        if applicant.has_written_test==True:
            raise CustomValidation(detail='sorry you have written this exam',field='job_id',)


        clean_data = general_job_serializer.TestQuetionFormatterSerializer(instance=job.job_test,many=False)

        data = response_data(status=200,message='success',data=clean_data.data)
        return Response(data,status=status.HTTP_200_OK)
    
    @action(methods=['get'],detail=False)
    def get_list_of_test(self,request,format=False):
        all_application = JobApplicant.objects.filter(jobseekers=request.user.jobseekerprofile,job__is_active=True,has_written_test=False)
        def get_jobid(job):return job.get('job')

        all_job_id = list(map(get_jobid,all_application.values('job')))
        jobs = Job.objects.filter(id__in=all_job_id,job_variant='filter_and_test')
        serialzier_class= job_seekers_serializer.JobandTestCleaner(jobs,many=True)

        return Response(data=serialzier_class.data,status=200)
    @action(methods=['get'],detail=False)
    def jobs_applied_for_list(self,request,format=None):
        job_applicant = JobApplicant.objects.filter(jobseekers=request.user.jobseekerprofile)

        cleaner = job_seekers_serializer.JobApplicantCleaner(instance=job_applicant,many=True)
        return Success_response('Success',data=cleaner.data)


class UploadCvViewSet(GenericViewSet,mixins.UpdateModelMixin):
    queryset = JobSeekerProfile.objects.all()
    permission_classes = [OnlyJobSeeker,]
    serializer_class  = job_seekers_serializer.UploadCvSerializer


    def update(self, request, *args, **kwargs):
        logged_in_user = request.user
        pk = kwargs['pk']
        print({
            "logged_in_user":logged_in_user.id,
            'pk':pk
        })
        if logged_in_user.jobseekerprofile.user.id !=int(pk):
            raise CustomValidation('Bad Request',field='pk',)
        return super().update(request, *args, **kwargs)

    def get_object(self):
        user_id = self.kwargs['pk']
        return get_object_or_404 (JobSeekerProfile,user=user_id)
    



class JobSeekerApplicationViewSet(viewsets.ViewSet):
    permission_classes = [OnlyJobSeeker,MustHaveCV]
    serializer_class  = job_seekers_serializer.JobSeekerApplicationSerailizer
    filterset_class = custom_filter.JobApplicantFilter
    def list(self,request,*args,**kwargs):
        queryset =  JobApplicant.objects.all()
        filter_set = self.filterset_class(request.query_params,queryset=queryset)
        clean_data =  self.serializer_class(filter_set.qs ,many=True)
        data = response_data(200,message='Successfully',data=clean_data.data)
        return Response(data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=['post'])
    def accept_offer(self,request,*args,**kwargs):
        job_applicant_id  = request.data.get('job_applicant_id')
        jobapplicant = get_object_or_404(JobApplicant,id=job_applicant_id)
        if jobapplicant.jobseekers.id  != request.user.jobseekerprofile.id:
            raise CustomValidation(detail='Permisson Denied',field='error')

        if jobapplicant.final_selection_state !='selected':
            raise CustomValidation(detail='You were not selected so you can accept an offer',field='error')
        jobapplicant.accept_application  =True
        jobapplicant.save()
        novu = NovuProvider()
        novu.send_notification(
        name='sequential-jobs-api',
        # telling the owner of the job that offer has been accepted
        sub_id=[jobapplicant.job.company.user.id],
        title=f'Offer Accepted',
        content=f'{jobapplicant.jobseekers.user.full_name} accept offer for {jobapplicant.job.job_title}' )

        return Success_response('Offer Accepted',data=[])
    
    @action(detail=False,methods=['post'])
    def upload_job_docs(self,request,*args,**kwargs):
        serialzer = job_seekers_serializer.JobSeekerUploadsJobDocs(data=request.data,context={'request'})

        serialzer.is_valid(raise_exception=True)
        serialzer.save()

        return Success_response('Done please hold on for validation',data=[])
    

class JobSeekerHandleDocs(viewsets.ViewSet):
    serializer_class = job_seekers_serializer.UploadJobApplicationDocmentationSerializer
    permission_classes = [OnlyJobSeeker,MustHaveCV]


    def create(self,request,*args,**kwargs):
        job_id = request.query_params.get('job_id',None)
        if job_id is None:
            raise CustomValidation(detail='add job_id to the query param')
        
        serliazer = self.serializer_class(data=request.data,context={
            'user':request.user,'id':job_id})
        return Success_response('upload docs successfully')

    def list(self,request,*args,**kwargs):
        job_id = request.query_params.get('job_id',None)
        if job_id is None:
            raise CustomValidation(detail='add job_id to the query param')
        job = Job.objects.get(id=job_id)

        return Success_response('Success',data=job.job_required_document.split(','))