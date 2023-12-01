from rest_framework import serializers
from jobs.models import (Job, JobApplicant, FilterQuetionFillInGap,
                         FilterQuetionOption, FilterQuetionMultiChoiceQuetion, JobApplicationDocmentation)
from jobs import models as jobs_models
from utils.exception import CustomValidation
from rest_framework import status
from myauthentication.models import JobSeekerProfile
from django.shortcuts import get_object_or_404


class JobCleanerForJobSeekerSerializer(serializers.ModelSerializer):
    org_name = serializers.SerializerMethodField()

    def get_org_name(self, job):
        return job.company.organisation_name

    class Meta:
        model = Job
        fields = ['id', 'job_title', 'is_active', 'money_sign', "employement_type",
                  'location', 'job_type', 'salary', 'currency',
                  'job_required_document', 'description', 'description_content',
                  'job_test', 'job_variant', 'job_filter', 'country', 'org_name'
                  ]


class JobApplicantCleaner(serializers.ModelSerializer):
    job = serializers.SerializerMethodField()

    def get_job(self, job_applicant):
        clean_job = JobCleanerForJobSeekerSerializer(
            instance=job_applicant.job, many=False)
        return clean_job.data

    class Meta:
        model = jobs_models.JobApplicant
        fields = [
            'id', 'job',
        ]


class UploadCvSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobSeekerProfile
        fields = ['cv',]


class ApplyForJobSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()

    def validate(self, attrs):
        job_id = attrs.get('job_id', -1)
        if self.context.get('request').user.user_type != 'job_seakers':
            raise CustomValidation(detail='You need to login as a job seeker',
                                   field='job_id', status_code=status.HTTP_400_BAD_REQUEST)
        if not Job.objects.filter(id=job_id).exists():
            raise CustomValidation(
                detail='Job Does Not Exist', field='job_id', status_code=status.HTTP_400_BAD_REQUEST)
        job_seeker = self.context.get('request').user.jobseekerprofile
        job = Job.objects.get(id=job_id)
        if JobApplicant.objects.filter(job=job, jobseekers=job_seeker).exists():
            raise CustomValidation(detail='You Have Applied already',
                                   field='job_id', status_code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    def create(self, validated_data):
        job_id = validated_data.get('job_id')
        job = Job.objects.get(id=job_id)
        job_seeker = self.context.get('request').user.jobseekerprofile

        job_application = JobApplicant.objects.create(
            jobseekers=job_seeker,
            job=job,
        )
        job_application.save()
        return job_application


class FillInTheGapHandlerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    answer = serializers.CharField()


class QuetionOptionHandlerSerilizer(serializers.Serializer):
    id = serializers.IntegerField()
    answer = serializers.CharField()


class QuetionMultiChoiceQuetionHandlerSerilizer(serializers.Serializer):
    id = serializers.IntegerField()
    answer = serializers.ListField()


class HandleQuetionMarkingSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    fill_in_the_gap = FillInTheGapHandlerSerializer(many=True)
    filter_quetion_option = QuetionOptionHandlerSerilizer(many=True)
    filter_quetion_multi_choice_quetion = QuetionMultiChoiceQuetionHandlerSerilizer(
        many=True)

    def validate(self, attrs):
        # endpoint to write exam ... cant write if he has not applyied
        job_id = attrs.get('job_id')
        user = self.context.get('request').user
        print(user.jobseekerprofile)
        if not JobApplicant.objects.filter(job__id=job_id, jobseekers=user.jobseekerprofile).exists():
            raise CustomValidation(
                detail='You have not applied for this job', field='job_id')

        # cant write twice
        applicant = JobApplicant.objects.filter(
            job__id=job_id, jobseekers=user.jobseekerprofile).first()
        if applicant.has_written_exam:
            CustomValidation(detail="You Can' write twice", field='job_id')
        return super().validate(attrs)

    def create(self, validated_data):
        # print(validated_data)
        fillInTheGap_result = self.markFillInTheGap(
            validated_data.get('fill_in_the_gap'))
        quetionOption_result = self.markFilterQuetionOption(
            validated_data.get('filter_quetion_option'))
        filterQuetionMultiChoiceQuetion = self.markFilterQuetionMultiChoiceQuetion(
            validated_data.get('filter_quetion_multi_choice_quetion'))

        "remove None"
        fillInTheGap_result = fillInTheGap_result if fillInTheGap_result is not None else 0
        quetionOption_result = quetionOption_result if quetionOption_result is not None else 0
        filterQuetionMultiChoiceQuetion = filterQuetionMultiChoiceQuetion if filterQuetionMultiChoiceQuetion is not None else 0

        user = self.context.get('request').user
        job_id = validated_data.get('job_id')
        applicant_form = JobApplicant.objects.filter(
            job__id=job_id, jobseekers=user.jobseekerprofile).first()
        applicant_form.has_written_exam = True
        applicant_form.filter_quetions_score = fillInTheGap_result + \
            quetionOption_result+filterQuetionMultiChoiceQuetion
        applicant_form.save()
        print({'applicant_form.filter_quetions_score':applicant_form.filter_quetions_score})

        return {
            'fillInTheGap_result': fillInTheGap_result,
            'quetionOption_result': quetionOption_result,
            'filterQuetionMultiChoiceQuetion': filterQuetionMultiChoiceQuetion,
            'job_variant': applicant_form.job.job_variant
        }

    def markFilterQuetionOption(self, data_list: list) -> int:
        count = 0
        for data in data_list:
            instance = FilterQuetionOption.objects.get(id=data.get('id'))

            if instance.mark_question(data.get('answer')):
                'Each Quetion has it mark'
                count = count + instance.quetion_mark
        return count

    def markFillInTheGap(self, data_list: list) -> int:
        count = 0
        for data in data_list:
            instance = FilterQuetionFillInGap.objects.get(id=data.get('id'))
            if instance.mark_question(data.get('answer')):
                'Each Quetion has it mark'
                count = count + instance.quetion_mark

        return count

    def markFilterQuetionMultiChoiceQuetion(self, data_list: list) -> int:
        count = 0
        for data in data_list:
            instance = FilterQuetionMultiChoiceQuetion.objects.get(
                id=data.get('id'))
            if instance.mark_question(data.get('answer')):
                'Each Quetion has it mark'
                count = count + instance.quetion_mark
            return count


class HandleTestMarkingSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    fill_in_the_gap = FillInTheGapHandlerSerializer(many=True)
    filter_quetion_option = QuetionOptionHandlerSerilizer(many=True)
    filter_quetion_multi_choice_quetion = QuetionMultiChoiceQuetionHandlerSerilizer(
        many=True)

    def validate(self, attrs):
        # endpoint to write exam ... cant write if he has not applyied
        job_id = attrs.get('job_id')
        user = self.context.get('request').user
        print(user.jobseekerprofile)
        if not JobApplicant.objects.filter(job__id=job_id, jobseekers=user.jobseekerprofile).exists():
            raise CustomValidation(
                detail='You have not applied for this job', field='job_id')

        # cant write twice
        applicant = JobApplicant.objects.filter(
            job__id=job_id, jobseekers=user.jobseekerprofile).first()
        if applicant.has_written_test:
            CustomValidation(detail="You Can' write twice", field='job_id')
        return super().validate(attrs)

    def create(self, validated_data):
        # print(validated_data)
        fillInTheGap_result = self.markFillInTheGap(
            validated_data.get('fill_in_the_gap'))
        quetionOption_result = self.markFilterQuetionOption(
            validated_data.get('filter_quetion_option'))
        filterQuetionMultiChoiceQuetion = self.markFilterQuetionMultiChoiceQuetion(
            validated_data.get('filter_quetion_multi_choice_quetion'))

        "remove None"
        fillInTheGap_result = fillInTheGap_result if fillInTheGap_result is not None else 0
        quetionOption_result = quetionOption_result if quetionOption_result is not None else 0
        filterQuetionMultiChoiceQuetion = filterQuetionMultiChoiceQuetion if filterQuetionMultiChoiceQuetion is not None else 0

        user = self.context.get('request').user
        job_id = validated_data.get('job_id')
        applicant_form = JobApplicant.objects.filter(
            job__id=job_id, jobseekers=user.jobseekerprofile).first()
        applicant_form.has_written_test = True
        applicant_form.filter_quetions_score = fillInTheGap_result + \
            quetionOption_result+filterQuetionMultiChoiceQuetion
        applicant_form.save()

        return {
            'fillInTheGap_result': fillInTheGap_result,
            'quetionOption_result': quetionOption_result,
            'filterQuetionMultiChoiceQuetion': filterQuetionMultiChoiceQuetion,
            'job_variant': applicant_form.job.job_variant
        }

    def markFilterQuetionOption(self, data_list: list) -> int:
        count = 0
        for data in data_list:

            instance = jobs_models.TestQuetionOption.objects.get(
                id=data.get('id'))

            if instance.mark_question(data.get('answer')):
                'Each Quetion has it mark'
                count = count + instance.quetion_mark
        return count

    def markFillInTheGap(self, data_list: list) -> int:
        count = 0
        for data in data_list:

            instance = jobs_models.TestQuetionFillInGap.objects.get(
                id=data.get('id'))
            if instance.mark_question(data.get('answer')):
                'Each Quetion has it mark'
                count = count + instance.quetion_mark

        return count

    def markFilterQuetionMultiChoiceQuetion(self, data_list: list) -> int:
        count = 0
        for data in data_list:

            instance = jobs_models.TestQuetionMultiChoiceQuetion.objects.get(
                id=data.get('id'))
            if instance.mark_question(data.get('answer')):
                'Each Quetion has it mark'
                count = count + instance.quetion_mark
            return count


class JobandTestCleaner(serializers.ModelSerializer):
    test_info = serializers.SerializerMethodField()

    def get_test_info(self, instance: Job):
        try:
            return {
                'title': instance.job_test.title,
                'job_id': instance.id,
                'org_name': instance.company.organisation_name,
                'short_org_name': instance.company.organisation_name_shortname
            }
        except:
            return None

    class Meta:
        fields = ['id', 'job_title', 'test_info']
        model = Job


class JobSeekerApplicationSerailizer(serializers.ModelSerializer):
    jobseekers = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    docs_needed = serializers.SerializerMethodField()
# """
# cadidate name
# date of application
# company name
# view offer letter
# upload documentation
# """

    def get_jobseekers(self, instance: jobs_models.JobApplicant):
        return {
            'name': instance.jobseekers.user.full_name, }

    def get_company(self, instance: jobs_models.JobApplicant):
        return {
            'id': instance.job.company.id,
            'name': instance.job.company.organisation_name,
            'job_title': instance.job.job_title,
            'job_id': instance.job.id
        }

    def get_docs_needed(self, instance: jobs_models.JobApplicant):
        return instance.job.job_required_document.split(',')

    class Meta:
        model = jobs_models.JobApplicant
        fields = ['id', 'generated_panelist_total_score',
                  'company', 'docs_needed', 'jobseekers',
                  'docs_needed', 'company', 'jobseekers', 'accept_application', 'final_selection_state']


class JobSeekerUploadsJobDocs(serializers.Serializer):
    applicant_id = serializers.IntegerField()
    all_file = serializers.ListField(
        child=serializers.FileField(max_length=10000000,
                                    allow_empty_file=False, use_url=False, write_only=True))

    def create(self, validated_data):
        all_files = validated_data.get('all_file')
        applicant_id = validated_data.get('applicant_id')
        applicant = get_object_or_404(JobApplicant, id=applicant_id)
        print({'all_files': all_files,
              'd': applicant.job.job_required_document.split(',')})
        if len(all_files) != len(applicant.job.job_required_document.split(',')):
            raise CustomValidation('Something is not right', field='error')
        for file in all_files:
            JobApplicationDocmentation.objects.create(
                job_applicant=applicant,
                name_of_file=file.name,
                file=file
            )
        return applicant


class JobsAppliedForCleaner(serializers.ModelSerializer):
    job = serializers.SerializerMethodField()
    candidates_applied = serializers.SerializerMethodField()

    # still usefull for jobs_test_taken endpoint
    # still usefull for jobs_test_scheduled for now endpoint
    def get_job(self, instance: JobApplicant):
        job_cleaner = JobCleanerForJobSeekerSerializer(instance=instance.job)
        return {
            'company_name': instance.job.company.organisation_name,
            'position': instance.job.job_title,
            'id': instance.job.id,
            'more_on_job': job_cleaner.data

        }

    def get_candidates_applied(self, instance: JobApplicant):
        return JobApplicant.objects.filter(job=instance.job).count()

    class Meta:
        model = JobApplicant
        fields = [
            'id', 'job',
            'final_selection_state', 'candidates_applied'
        ]


class JobsTestTakenSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobApplicant
        fields = [

        ]


class UploadJobApplicationDocmentationSerializer:

    def __init__(self, data, context=dict()) -> None:
        self.data = data
        self.context = context
        self.validate()
        self.create(data)

    def validate(self) -> None:
        if self.context.get('id', None) is None:
            raise CustomValidation(
                detail='Please pass in id of Job model', field='error')
        job = Job.objects.get(id=self.context.get('id'))
        keys = self.data.keys()
        if job.validate_job_required_document(list(keys)) == False:
            print({'frontend data': self.data})
            raise CustomValidation(
                detail='Please check the file and try again', field='error')

    def create(self, validated_data):
        user = self.context.get('user')
        keys = validated_data.keys()
        job = Job.objects.get(id=self.context.get('id'))

        applicant = JobApplicant.objects.get(
            jobseekers=user.jobseekerprofile, job=job)
        for key in keys:
            docs, _ = JobApplicationDocmentation.objects.get_or_create(
                name_of_file=key,
                job_applicant=applicant
            )
            docs.file = validated_data[key]
            docs.save()
        return dict()
