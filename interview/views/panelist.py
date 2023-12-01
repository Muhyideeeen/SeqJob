from rest_framework import viewsets,status
from rest_framework.response import Response
from myauthentication import permissions
from ..  import models as interview_models
from interview.serializers import panelist as panelist_serializers
from jobs import models as job_models
from jobs.serializers import panelist as panlist_job_serialzier
from utils.response_data import response_data
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

class PanelistHandlesInterview(viewsets.ViewSet):
    permission_classes = [permissions.OnlyPanelist]
    serializer_class = panlist_job_serialzier.PanelistJobCleanerSerializer

    def list(self,request,format=None):
        # the logged in user has to be a panelist
        jobs = request.user.panelistprofile.job.all()
        serialized =self.serializer_class(instance=jobs,many=True)
        
        data = response_data(200,message='Successful',data=serialized.data)
        return Response(data,status=status.HTTP_201_CREATED)
    
    # rating job seekers
    @action(methods=['post'],detail=False)
    def rating_job_seekers(self,request,*args,**kwargs):
        "here theb panelist can rate a job seeker"
        serialized = panelist_serializers.PanelistRateJobSeekeers(
            data=request.data,context={'request':request})
         
        serialized.is_valid(raise_exception=True)
        candidate_sheet = serialized.save()
        print(candidate_sheet)
        clean_data = panelist_serializers.CandidateInterviewSheetCleanerSerializer(instance=candidate_sheet,many=False)
        data = response_data(201,message='Rated',data=clean_data.data)
        return Response(data,status=status.HTTP_201_CREATED)

    @action(methods=['post'],detail=False,permission_classes=[permissions.CompanyAndPanelist])
    def get_rating_sheet(self,request,*args,**kwargs):
        job_applicant_id= request.data.get('job_applicant',-1)
        job_id= request.data.get('job_id',-1)


        job = get_object_or_404(job_models.Job,id=job_id)
        job_applicant = get_object_or_404(job_models.JobApplicant,id=job_applicant_id)
        sheet,created = interview_models.CandidateInterviewSheet.objects.get_or_create(
            interview = job.interview,
            job_seeker = job_applicant.jobseekers,
            panelist=request.user.panelistprofile
        )
        if created:
            sheet.rating_sheet= job.interview.rating_sheet
            sheet.save()
        clean_data = panelist_serializers.CandidateInterviewSheetCleanerSerializer(instance=sheet,many=False)
        data = response_data(200,message='Success',data=clean_data.data)
        return Response(data,status=status.HTTP_200_OK)


    @action(methods=['post'],detail=False)
    def interview_aggregate(self,request,format=None):
        job_id = request.data.get('job_id',-1)

        job = get_object_or_404(job_models.Job,id=job_id)
        rating_sheet_header = job.interview.rating_sheet

        all_candidate_sheets = interview_models.CandidateInterviewSheet.objects.filter(
            interview = job.interview
        )
        

        def clean_header(header):return header.get('name')

        headers = list(map(clean_header,rating_sheet_header))
        result = dict()
        results = []
        for head1 in headers:
            result[head1]=0
        for head in headers:
            for sheet in all_candidate_sheets:
                for rating_sheet in sheet.rating_sheet:
                    if head == rating_sheet.get('value'):
                        results.append(
                            {
                                'value':head,
                                'aggrate_rating':result[head]+ rating_sheet.get('score'),
                                'cut_off':rating_sheet.get('cut_off',0)
                            }
                        )

        def get_all_values(data):return data.get('value')
        
        'get all the values and remove all the duplicates'
        all_values = list(set(map(get_all_values,results)))
        clean_data = []

        for value in all_values:
            data = dict()
            data['value'] = value
            data['aggrate_rating'] = 0
            data['cut_off'] = 0
                # clean_data.append                
            for result in results:
                if value == result.get('value'):
                    data['aggrate_rating'] = data['aggrate_rating'] + result.get('aggrate_rating')
                    data['cut_off'] = data['cut_off'] + result.get('cut_off')
            clean_data.append(data)

        data = response_data(200,message='Rated',data=clean_data)
        return Response(data,status=status.HTTP_200_OK)



    @action(methods=['post'],detail=False)
    def get_interview_aggregate_breakdown(self,request,format=None):
        job_id = request.data.get('job_id',-1)
        job = get_object_or_404(job_models.Job,id=job_id)
        all_candidate_sheets = interview_models.CandidateInterviewSheet.objects.filter(
            interview = job.interview
        )
        clean_data = panelist_serializers.PanelistAggregateCleaner(all_candidate_sheets,many=True)


        data = response_data(200,message='Successful',data=clean_data.data)
        return Response(data,status=status.HTTP_200_OK)