from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from myauthentication.permissions import OnlyCompany, OnlyPanelist,CompanyAndPanelist
from jobs.serializers import company as company_job_serializer
from utils.response_data import response_data
from rest_framework import status
from rest_framework.parsers import FormParser
from jobs import models as companyjob_models
from utils.custom_parsers import NestedMultipartParser
from rest_framework.decorators import action
from utils.exception import CustomValidation
from django.shortcuts import get_object_or_404
from .. import filter as custom_filters
from mailing.EmailConfirmation import invite_job_seeker
from myauthentication import models as auth_models
from utils.custom_response import Success_response
from utils.custom_pagination import CustomPagination


class CompanyManageJobs(viewsets.ViewSet):
    permission_classes = [CompanyAndPanelist]
    parser_classes = (NestedMultipartParser, FormParser,)
    serializer_class = company_job_serializer.CompanyManageJobSerializer
    filterset_class = custom_filters.JobFIlter
    pagination_class = CustomPagination

    @action(methods=['get'], detail=False, permission_classes=[OnlyCompany])
    def total_applicant(self, request, *args, **kwargs):
        filter_job_id = request.GET.get("filter_job_id", None)

        total_applicant = companyjob_models.JobApplicant.objects.filter(
            job__company=request.user.companyprofile
        )

        if filter_job_id:
            total_applicant = companyjob_models.JobApplicant.objects.filter(
                job__company=request.user.companyprofile, job=filter_job_id
            )

        serializer = company_job_serializer.JobApplicantDashboardSerializerCleaner(
            instance=total_applicant, many=True
        )
        data = response_data(200, message='Successfully', data=serializer.data)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, permission_classes=[OnlyCompany])
    def applicant_hired(self, request, *args, **kwargs):
        filter_job_id = request.GET.get("filter_job_id", None)

        applicant_hired = companyjob_models.JobApplicant.objects.filter(
            job__company=request.user.companyprofile, final_selection_state='selected'
        )

        if filter_job_id:
            applicant_hired = companyjob_models.JobApplicant.objects.filter(
                job__company=request.user.companyprofile, job=filter_job_id, final_selection_state='selected'
            )

        serializer = company_job_serializer.JobApplicantDashboardSerializerCleaner(
            instance=applicant_hired, many=True
        )
        data = response_data(200, message='Successfully', data=serializer.data)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, permission_classes=[OnlyCompany])
    def total_job_post(self, request, *args, **kwargs):
        total_number_of_job_post = companyjob_models.Job.objects.filter(
            company=request.user.companyprofile)
        serializer = company_job_serializer.CompanyManageJobSerializer(
            instance=total_number_of_job_post, many=True
        )
        data = response_data(200, message='Successfully', data=serializer.data)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, permission_classes=[OnlyCompany])
    def company_dashboard_summary(self, request, *args, **kwargs):
        total_applicant = companyjob_models.JobApplicant.objects.filter(
            job__company=request.user.companyprofile
        ).count()
        applicant_hired = companyjob_models.JobApplicant.objects.filter(
            job__company=request.user.companyprofile, final_selection_state='selected'
        ).count()
        total_number_of_job_post = companyjob_models.Job.objects.filter(
            company=request.user.companyprofile).count()
        closed_jobs = companyjob_models.Job.objects.filter(
            company=request.user.companyprofile, is_active=False).count()
        total_number_of_cv = companyjob_models.JobApplicant.objects.filter(
            job__company=request.user.companyprofile).count()
        active_jobs = companyjob_models.Job.objects.filter(
            company=request.user.companyprofile, is_active=True).count()

        clean_data = {
            'total_applicant': total_applicant,
            'applicant_hired': applicant_hired,
            'total_number_of_job_post': total_number_of_job_post,
            'closed_jobs': closed_jobs,
            'total_number_of_cv': total_number_of_cv,
            'active_jobs': active_jobs
        }
        data = response_data(
            201, message='Created Job Successfully', data=clean_data)
        return Response(data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        job = get_object_or_404(companyjob_models.Job, id=kwargs.get('pk', -1))

        if job.job_variant == 'filter_only':
            if job.job_filter is None:
                raise CustomValidation(detail='please set quetions for the job',
                                       field='error', status_code=status.HTTP_401_UNAUTHORIZED)
        if job.job_variant == 'filter_and_test':
            if job.job_test is None:
                raise CustomValidation(detail='please set test for the job',
                                       field='error', status_code=status.HTTP_401_UNAUTHORIZED)
            if job.job_filter is None:
                raise CustomValidation(detail='please set quetions for the job',
                                       field='error', status_code=status.HTTP_401_UNAUTHORIZED)

        serailzer = self.serializer_class(
            data=request.data, instance=job, partial=True)
        serailzer.is_valid(raise_exception=True)
        data = serailzer.save()
        return Success_response('Update', data=[], status_code=status.HTTP_200_OK)

    def create(self, request, pk=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=request.user.companyprofile)
        data = response_data(
            201, message='Created Job Successfully', data=serializer.data)
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        job = get_object_or_404(companyjob_models.Job, id=pk)
        clean_data = self.serializer_class(job)
        data = response_data(200, message='Success', data=clean_data.data)
        return Response(data, status=status.HTTP_200_OK)

    def list(self, request, pk=None):
        if request.user.user_type=='company':
            jobs = companyjob_models.Job.objects.filter(
                company=request.user.companyprofile)
        else:
            # then the person is a panelist
            jobs =  request.user.panelistprofile.job.all()
        filter_set = self.filterset_class(request.query_params, queryset=jobs)
        clean_data = self.serializer_class(filter_set.qs, many=True)
        data = response_data(200, message='Successfully', data=clean_data.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[OnlyCompany])
    def delete(self, request, *args, **kwargs):
        pk = request.data.get('pk', None)
        if pk is None:
            raise CustomValidation(detail='enter job id', field='error')
        job = get_object_or_404(companyjob_models.Job, id=pk)
        if job.company.id != request.user.companyprofile.id:
            raise CustomValidation(
                detail='you dont have permission', field='error')
        job.delete()
        return Success_response(msg='Deleted Successfully', status_code=status.HTTP_202_ACCEPTED)

    @action(methods=['post'], detail=False, permission_classes=[OnlyCompany])
    def invite_candidate(self, *args, **Kwargs):
        serialzed = company_job_serializer.InviteCandidateSerializer(
            data=self.request.data, context={'request': self.request})
        serialzed.is_valid(raise_exception=True)
        list_of_invited_ids = serialzed.save()
        data = response_data(200, message='Successfully', data={
                             'list_of_invited_ids': list_of_invited_ids})
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[])
    def switch_job_on(self, *args, **kwargs):
        job_id = self.request.data.get('job_id', None)
        switch = self.request.data.get('switch', 'False')
        job = get_object_or_404(companyjob_models.Job, id=job_id)
        print({'switch': switch})
        if switch == 'True':
            job.is_active = True
            job.save()

        else:
            job.is_active = False
            job.save()
        data = response_data(
            200, message='Job Updated Succeffully', data={'switch': switch})
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[OnlyCompany | OnlyPanelist])
    def get_sorted_job_candidate(self, *args, **kwargs):
        job_id = self.request.data.get('job_id', None)
        Status = self.request.data.get('status', 'suitable')
        if job_id is None:
            raise CustomValidation(detail='job_id is missing', field='job_id')
        job = companyjob_models.Job.objects.get(id=job_id)

        application = companyjob_models.JobApplicant.objects.filter(job=job)
        if Status == 'suitable':
            application = application.filter(
                filter_quetions_score__gte=job.job_filter.suitable,
                filter_quetions_score__lte=job.job_filter.end_suitable,
            )
        if Status == 'partially_suitable':
            application = application.filter(
                filter_quetions_score__gte=job.job_filter.partially_suitable,
                filter_quetions_score__lte=job.job_filter.end_partially_suitable,
            )
        if Status == 'not_suitable':
            application = application.filter(
                filter_quetions_score__gte=job.job_filter.not_suitable,
                filter_quetions_score__lte=job.job_filter.end_not_suitable,
            )
        # greater than or  equal to suitable and lesser that or equal to end_suitable

        clean_data = company_job_serializer.SortJobCandidateSerializer(
            application, many=True)

        data = response_data(200, message='Successfully', data=clean_data.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[OnlyCompany | OnlyPanelist])
    def get_sorted_job_candidate_test(self, *artgs, **kwargs):
        job_id = self.request.data.get('job_id', None)
        Status = self.request.data.get('status', 'suitable')
        if job_id is None:
            raise CustomValidation(detail='job_id is missing', field='job_id')
        job = companyjob_models.Job.objects.get(id=job_id)

        if not job.job_test:
            raise CustomValidation(
                detail="no test assesment for this job", field="job_test")

        application = companyjob_models.JobApplicant.objects.filter(job=job)
        if Status == 'suitable':
            application = application.filter(
                filter_quetions_score__gte=job.job_test.suitable,
                filter_quetions_score__lte=job.job_test.end_suitable,
            )
        if Status == 'partially_suitable':
            application = application.filter(
                filter_quetions_score__gte=job.job_test.partially_suitable,
                filter_quetions_score__lte=job.job_test.end_partially_suitable,
            )
        if Status == 'not_suitable':
            application = application.filter(
                filter_quetions_score__gte=job.job_test.not_suitable,
                filter_quetions_score__lte=job.job_test.end_not_suitable,
            )
        # greater than or  equal to suitable and lesser that or equal to end_suitable

        clean_data = company_job_serializer.SortJobCandidateSerializer(
            application, many=True)

        data = response_data(200, message='Successfully', data=clean_data.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[OnlyCompany | OnlyPanelist])
    def get_candidate_docs(self, *args, **kwargs):
        applicant_id = self.request.data.get('applicant_id', None)

        applicant = get_object_or_404(
            companyjob_models.JobApplicant, id=applicant_id)
        data = companyjob_models.JobApplicationDocmentation.objects.filter(
            job_applicant=applicant)
        clean_data = company_job_serializer.CompanyCandidatesDocsCleaner(
            instance=data, many=True)
        data = response_data(200, message='Success', data=clean_data.data)
        return Response(data, status=status.HTTP_200_OK)


class CompanyManageQuetions(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, OnlyCompany]
    serializer_class = company_job_serializer.CompanyManageJobFilterQuetionSerializer
    # parser_classes = (NestedMultipartParser,FormParser,)

    def get_permissions(self):
        return super().get_permissions()

    @action(methods=['post'], detail=False)
    def set_cut_off_for_quetion(self, request, *args, **kwargs):
        pk = request.data.get('id', -1)
        instance = get_object_or_404(companyjob_models.JobFilterQuetion, id=pk)
        serialized = company_job_serializer.SetCutOffForQuetion(
            instance=instance, data=request.data, context={'request': request})
        serialized.is_valid(raise_exception=True)
        serialized.save()
        data = response_data(200, message='Succesffully added', data=[])
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_cut_off_for_quetion(self, request, *args, **Kwargs):
        print(Kwargs)
        pk = Kwargs.get('pk')
        instance = get_object_or_404(companyjob_models.JobFilterQuetion, id=pk)
        #
        serialized = company_job_serializer.SetCutOffForQuetionCleaner(
            instance, many=False)
        data = response_data(
            200, message='Succesffully added', data=serialized.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def add_qeution_to_job(self, request, *args, **kwargs):
        serialized = company_job_serializer.AddQuetionToJob(
            data=request.data, context={'request': request})
        serialized.is_valid(raise_exception=True)
        serialized.save()
        data = response_data(200, message='Succesffully added', data=[])
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,)
    def list_qeutions(self, request, *args, **kwargs):
        job_filter_quetion = companyjob_models.JobFilterQuetion.objects.filter(
            company=request.user.companyprofile)
        data = company_job_serializer.AddQuetionToJob(
            instance=job_filter_quetion, many=True)
        # data.is_valid(raise_exception=True)
        # data.save()
        data = response_data(200, message='Successfull', data=data.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,)
    def get_job_filter_questions(self, request, *args, **kwargs):
        job_id = int(request.GET.get("job_id", -1))

        job = get_object_or_404(
            companyjob_models.Job, id=job_id)

        if not job.job_filter:
            raise CustomValidation(field="job_id", detail="invalid job")

        job_filter_id = job.job_filter.pk

        job_filter = companyjob_models.JobFilterQuetion.objects.get(
            id=job_filter_id)
        data = company_job_serializer.GetJobFiltersSerializer(job_filter)
        data = response_data(200, message="Successfull", data=data.data)

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = response_data(
            201, message='Created Question Successfully', data=[serializer.data])
        return Response(data, status=status.HTTP_201_CREATED)


class CompanyManageTest(viewsets.ViewSet):
    'Test is not same with filterjob!'

    permission_classes = [permissions.IsAuthenticated, OnlyCompany]
    serializer_class = company_job_serializer.CompanyManageJobFTestSerializer

    def get_permissions(self):
        return super().get_permissions()

    @action(methods=['post'], detail=False)
    def set_cut_off_for_quetion(self, request, *args, **kwargs):
        pk = request.data.get('id', -1)
        instance = get_object_or_404(companyjob_models.JobTestQuetion, id=pk)
        serialized = company_job_serializer.SetCutOffForTest(
            instance=instance, data=request.data, context={'request': request})
        serialized.is_valid(raise_exception=True)
        serialized.save()
        data = response_data(200, message='Succesffully added', data=[])
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_cut_off_for_quetion(self, request, *args, **Kwargs):
        print(Kwargs)
        pk = Kwargs.get('pk')
        instance = get_object_or_404(companyjob_models.JobTestQuetion, id=pk)
        #
        serialized = company_job_serializer.SetCutOffForJobTestCleaner(
            instance, many=False)
        data = response_data(
            200, message='Succesffully added', data=serialized.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def add_qeution_to_job(self, request, *args, **kwargs):
        serialized = company_job_serializer.AddTestToJob(
            data=request.data, context={'request': request})
        serialized.is_valid(raise_exception=True)
        serialized.save()
        data = response_data(200, message='Succesffully added', data=[])
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,)
    def list_qeutions(self, request, *args, **kwargs):
        job_filter_quetion = companyjob_models.JobTestQuetion.objects.filter(
            company=request.user.companyprofile)
        data = company_job_serializer.AddTestToJob(
            instance=job_filter_quetion, many=True)
        # data.is_valid(raise_exception=True)
        # data.save()
        data = response_data(200, message='Successfull', data=data.data)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,)
    def get_job_test_questions(self, request, *args, **kwargs):
        job_id = int(request.GET.get("job_id", -1))

        job = get_object_or_404(
            companyjob_models.Job, id=job_id)

        if not job.job_test:
            raise CustomValidation(field="job_id", detail="invalid job")

        job_test_id = job.job_test.pk

        job_test = companyjob_models.JobTestQuetion.objects.get(id=job_test_id)
        data = company_job_serializer.GetJobTestsSerializer(job_test)
        data = response_data(200, message="Successfull", data=data.data)

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = response_data(
            201, message='Created Question Successfully', data=serializer.data)
        return Response(data, status=status.HTTP_201_CREATED)


class GenerateJobFinalResult(viewsets.ViewSet):
    permission_classes = [
        permissions.IsAuthenticated, OnlyCompany | OnlyPanelist]
    serializer_class = company_job_serializer.GenerateJobFinalResultSerializer

    def create(self, request, pk=None):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        d = serializer.save()
        data = response_data(201, message='Generated Success', data=d)
        return Response(data, status=status.HTTP_201_CREATED)

    def list(self, request, pk=None):
        filter_by_offers_sent = request.query_params.get('offers_sent', None)
        jobseeker_acccept_offer = request.query_params.get('jobseeker_acccept_offer', None)
        job = get_object_or_404(companyjob_models.Job,
                                id=request.query_params.get('job_id', -1))
        if filter_by_offers_sent:
            allJobApplicants = companyjob_models.JobApplicant.objects.filter(
                job=job, final_selection_state='selected')
        elif jobseeker_acccept_offer:
            allJobApplicants = companyjob_models.JobApplicant.objects.filter(
                job=job,accept_application=True)
        else:
            allJobApplicants = companyjob_models.JobApplicant.objects.filter(
                job=job)

        clean_data = company_job_serializer.JobApplicantDashboardSerializerCleaner(
            allJobApplicants, many=True)

        data = response_data(200, message=' Success', data=clean_data.data)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False)
    def get_jobseeker_finial_result(self, request, pk=None):
            applicants = companyjob_models.JobApplicant.objects.get(id=request.query_params.get('job_seeker_id', -1))
            clean_data = company_job_serializer.JobApplicantDashboardSerializerCleaner(
            applicants, many=False)
            data = response_data(200, message=' Success', data=clean_data.data)
            return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def send_final_letters(self, request, pk=None):
        "endpoint to send letters to the right people"

        serialed = company_job_serializer.SendFinalLetters(
            data=request.data, context={'request': request})
        serialed.is_valid(raise_exception=True)
        serialed.save()
        return Success_response(msg='Letters Sent!', data=[])


class JobInvitationLetterView(generics.ListCreateAPIView):
    serializer_class = company_job_serializer.InvitationLetterSerializer
    permission_classes = [permissions.IsAuthenticated, OnlyCompany]

    def perform_create(self, serializer):
        return serializer.save(company=self.request.user.companyprofile)

    def create(self, request):
        body = request.data
        serializer = self.serializer_class(
            data=body, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer=serializer)
        return Success_response(msg="invitation created", data=serializer.data)

    def get_queryset(self):
        return companyjob_models.JobInvitationLetter.objects.filter(company=self.request.user.companyprofile)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Success_response(msg="Job invitation letters", data=serializer.data)


class JobInvitationLetterDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    serializer_class = company_job_serializer.InvitationLetterSerializer
    permission_classes = [permissions.IsAuthenticated, OnlyCompany]

    def get_queryset(self):
        return companyjob_models.JobInvitationLetter.objects.filter(company=self.request.user.companyprofile)


class FindJobsInvitationView(generics.GenericAPIView):
    serializer_class = company_job_serializer.InvitationLetterSerializer
    permission_classes = [permissions.IsAuthenticated, OnlyCompany]

    def get(self, request, jobId=None):
        job_invitation_letter = get_object_or_404(
            companyjob_models.JobInvitationLetter, job=jobId)
        serializer = self.serializer_class(job_invitation_letter)
        return Success_response(data=serializer.data, msg=f"invitation letter for job with the id of {jobId}")


class GetCVDetailsView(generics.GenericAPIView):
    serializer_class = company_job_serializer.GetCVDetailsSerializer
    permission_classes = [permissions.IsAuthenticated, OnlyCompany]

    def get(self, request, id=None):
        if not id:
            raise CustomValidation(
                detail="not found", field="id url path", status_code=status.HTTP_404_NOT_FOUND)

        job_seeker_details = get_object_or_404(
            auth_models.JobSeekerProfile, id=id)
        serializer = self.serializer_class(job_seeker_details)
        return Success_response(msg="job seeker details", data=serializer.data)


class GetAllCompanyRelatedCVsView(generics.GenericAPIView):
    serializer_class = company_job_serializer.JobApplicantDashboardSerializerCleaner
    permission_classes = [permissions.IsAuthenticated, OnlyCompany]

    def get(self, request):
        jobApplicants = companyjob_models.JobApplicant.objects.filter(
            job__company=request.user.companyprofile)

        serializer = self.serializer_class(jobApplicants, many=True)
        return Success_response(msg="all cvs related to this company", data=serializer.data)
