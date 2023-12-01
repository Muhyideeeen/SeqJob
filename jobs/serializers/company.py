from rest_framework import serializers
from jobs import models as companyjob_models
from interview.models import TrackCandidateInterviewInvitation
from rest_framework import serializers, status
from utils.exception import CustomValidation
from django.shortcuts import get_object_or_404
from myauthentication import models as auth_models
from interview import models as interview_models
from mailing.tasks import handle_invite_job_seeker
from django.shortcuts import get_object_or_404
from utils.job_categories import job_categories
from drf_extra_fields.fields import Base64ImageField


class SetCutOffForQuetionCleaner(serializers.ModelSerializer):

    class Meta:
        model = companyjob_models.JobFilterQuetion
        fields = '__all__'


class SetCutOffForQuetion(serializers.Serializer):
    not_suitable = serializers.IntegerField()
    end_not_suitable = serializers.IntegerField()

    partially_suitable = serializers.IntegerField()
    end_partially_suitable = serializers.IntegerField()

    suitable = serializers.IntegerField()
    end_suitable = serializers.IntegerField()

    def update(self, instance: companyjob_models.JobFilterQuetion, validated_data):
        # before we update we need to validate if this comapany owns the quetion

        if instance.company.user.id != self.context.get('request').user.id:
            raise CustomValidation(
                detail='UnAuthorized', status_code=status.HTTP_401_UNAUTHORIZED, field='error')
        instance.not_suitable = validated_data.get(
            'not_suitable', instance.not_suitable)
        instance.end_not_suitable = validated_data.get(
            'end_not_suitable', instance.end_not_suitable)

        instance.partially_suitable = validated_data.get('partially_suitable',)
        instance.end_partially_suitable = validated_data.get(
            'end_partially_suitable')

        instance.suitable = validated_data.get('suitable', 0)
        instance.end_suitable = validated_data.get('end_suitable', 0)

        instance.save()
        return instance


class CompanyManageJobSerializer(serializers.ModelSerializer):

    org_name = serializers.SerializerMethodField()

    def get_org_name(self, job):
        return job.company.organisation_name

    class Meta:
        model = companyjob_models.Job
        fields = ['id', 'job_title', 'is_active', 'location', 'job_type', 'salary', 'currency',
                  'job_required_document', 'description', 'job_filter', 'description_content',
                  'job_variant', 'job_test', 'country', 'org_name',
                  'job_categories', 'employement_type', 'money_sign', 'required_experience', 'generic_skills', 'technical_skills', 'professional_path', "created_at", "updated_at"
                  ]


class ListFilterQuetionFillInGapSerializer(serializers.Serializer):
    quetion = serializers.CharField()
    answer = serializers.CharField()
    quetion_mark = serializers.IntegerField()
    image = Base64ImageField()


class ListFilterQuetionOptionSerializer(serializers.Serializer):
    quetion = serializers.CharField()
    option_to_choose_from = serializers.JSONField()
    answer = serializers.CharField()
    quetion_mark = serializers.IntegerField()
    image = Base64ImageField()


class ListFilterQuetionMultiChoiceQuetionSerializer(serializers.Serializer):
    quetion = serializers.CharField()
    option_to_choose_from = serializers.JSONField()
    answer = serializers.JSONField()
    quetion_mark = serializers.IntegerField()
    image = Base64ImageField()


class CompanyManageJobFilterQuetionSerializer(serializers.Serializer):
    title = serializers.CharField()
    fill_in_gap_quetion = ListFilterQuetionFillInGapSerializer(many=True)
    option_quetion = ListFilterQuetionOptionSerializer(many=True)
    multi_choice_quetion = ListFilterQuetionMultiChoiceQuetionSerializer(
        many=True)
    job_filter_question_id = serializers.CharField(read_only=True)

    def bulkCreateFilterQuetionFillInGap(self, data, job_filter_quetionInstance):
        for i in data:
            clean_data = dict(i)
            companyjob_models.FilterQuetionFillInGap.objects.create(
                job_filter_quetion=job_filter_quetionInstance,
                quetion=clean_data.get('quetion'),
                answer=clean_data.get('answer'),
                quetion_mark=clean_data.get('quetion_mark'),
                image=clean_data.get('image')

            )

    def bulkCreateFilterOptionQuetion(self, data, job_filter_quetionInstance):
        for i in data:
            clean_data = dict(i)
            companyjob_models.FilterQuetionOption.objects.create(
                job_filter_quetion=job_filter_quetionInstance,
                quetion=clean_data.get('quetion'),
                anwser=clean_data.get('answer'),
                option_to_choose_from=clean_data.get('option_to_choose_from'),
                quetion_mark=clean_data.get('quetion_mark'),
                image=clean_data.get('image')


            )

    def bulkCreateFilterMultiChoiceQuetion(self, data, job_filter_quetionInstance):
        for i in data:
            clean_data = dict(i)
            companyjob_models.FilterQuetionMultiChoiceQuetion.objects.create(
                job_filter_quetion=job_filter_quetionInstance,
                quetion=clean_data.get('quetion'),
                anwser=clean_data.get('answer'),
                option_to_choose_from=clean_data.get('option_to_choose_from'),
                quetion_mark=clean_data.get('quetion_mark'),
                image=clean_data.get('image')


            )

    def create(self, validated_data):
        title = validated_data.get('title')
        list_of_fill_in_gap_quetion = validated_data.get(
            'fill_in_gap_quetion', [])
        list_of_option_quetion = validated_data.get('option_quetion', [])
        multi_choice_quetion = validated_data.get('multi_choice_quetion', [])
        company = self.context.get('request').user.companyprofile
        job_filter_quetion = companyjob_models.JobFilterQuetion.objects.create(
            title=title, company=company)
        job_filter_quetion.save()

        self.bulkCreateFilterQuetionFillInGap(
            list_of_fill_in_gap_quetion, job_filter_quetion)
        self.bulkCreateFilterOptionQuetion(
            list_of_option_quetion, job_filter_quetion)
        self.bulkCreateFilterMultiChoiceQuetion(
            multi_choice_quetion, job_filter_quetion)

        return {"job_filter_question_id": job_filter_quetion.pk, **validated_data}
        # return job_filter_quetion


class AddQuetionToJob(serializers.ModelSerializer):

    job_id = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField()

    def create(self, validated_data):
        job_filter_quetion_id = validated_data.get('id',)
        job_id = validated_data.get('job_id',)
        job_filter_quetion = companyjob_models.JobFilterQuetion.objects.get(
            id=job_filter_quetion_id)
        job = companyjob_models.Job.objects.get(id=job_id)
        job.job_filter = job_filter_quetion
        job.save()
        return job

    def validate(self, attrs):
        job_filter_quetion_id = attrs.get('id', -1)
        job_id = attrs.get('job_id', -1)
        if not companyjob_models.JobFilterQuetion.objects.filter(id=job_filter_quetion_id).exists():
            raise CustomValidation(detail='Quetion Does Not exist',
                                   field='id')
        if not companyjob_models.Job.objects.filter(id=job_id).exists():
            raise CustomValidation(detail='Job Does Not exist', field='job_id')
        return super().validate(attrs)

    class Meta:
        model = companyjob_models.JobFilterQuetion
        fields = ['id', 'title', 'job_id']


class SortJobCandidateSerializer(serializers.ModelSerializer):
    jobseekers = serializers.SerializerMethodField()
    maximun_test_score = serializers.SerializerMethodField()
    maximun_filter_score = serializers.SerializerMethodField()

    def get_maximun_test_score(self, instance: companyjob_models.JobApplicant):
        testScore = instance.job.job_test.suitable if instance.job.job_test else None
        return testScore

    def get_maximun_filter_score(self, instance: companyjob_models.JobApplicant):
        filterQuestionScore = instance.job.job_filter.suitable if instance.job.job_filter else None
        return filterQuestionScore

    def get_jobseekers(self, instance: companyjob_models.JobApplicant):
        cv_url = ''
        try:
            cv_url = instance.jobseekers.cv.url
        except:
            cv_url = ''
        return {
            'cv_url': cv_url,
            'jobseekers_id': instance.jobseekers.id,
            'email': instance.jobseekers.user.email,
            'full_name': instance.jobseekers.user.full_name,
            'role_applied_for': instance.job.job_title,
            'interview_result': instance.generated_panelist_total_score,
            'user_id': instance.jobseekers.user.id,
            'created_at': instance.created_at
        }

    class Meta:
        model = companyjob_models.JobApplicant
        fields = [
            'id',
            'jobseekers',
            "has_mail_sent",
            "maximun_test_score",
            "maximun_filter_score",
            'filter_quetions_score',
            'test_quetions_score',
            'job',

        ]


class InviteCandidateSerializer(serializers.Serializer):
    list_of_id = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        ids = validated_data.get('list_of_id', [])
        for id in ids:
            job_applicant = get_object_or_404(
                companyjob_models.JobApplicant, id=id)
            try:
                a = job_applicant.job.interview
            except:
                raise CustomValidation(detail='Please set an interview before inviting candidate',
                                       status_code=status.HTTP_400_BAD_REQUEST, field='error')

            if job_applicant.has_mail_sent == False:
                job_applicant.has_mail_sent = True
                job_applicant.save()
                TrackCandidateInterviewInvitation.objects.create(
                    job_seeker=job_applicant.jobseekers,
                    interview=job_applicant.job.interview,
                    has_mail_sent=True
                )
                handle_invite_job_seeker.delay(job_applicant.jobseekers.user.id, job_applicant.jobseekers.user.email,
                                               job_applicant.job.company.organisation_name
                                               )

        return ids


'the code below has to do with TestQuetion Realtionships with jobs*-'


class SetCutOffForJobTestCleaner(serializers.ModelSerializer):

    class Meta:
        model = companyjob_models.JobTestQuetion
        fields = '__all__'


class SetCutOffForTest(serializers.Serializer):
    not_suitable = serializers.IntegerField()
    end_not_suitable = serializers.IntegerField()

    partially_suitable = serializers.IntegerField()
    end_partially_suitable = serializers.IntegerField()

    suitable = serializers.IntegerField()
    end_suitable = serializers.IntegerField()

    def update(self, instance: companyjob_models.JobTestQuetion, validated_data):
        # before we update we need to validate if this comapany owns the quetion

        if instance.company.user.id != self.context.get('request').user.id:
            raise CustomValidation(
                detail='UnAuthorized', status_code=status.HTTP_401_UNAUTHORIZED, field='error')
        instance.not_suitable = validated_data.get(
            'not_suitable', instance.not_suitable)
        instance.end_not_suitable = validated_data.get(
            'end_not_suitable', instance.end_not_suitable)

        instance.partially_suitable = validated_data.get('partially_suitable',)
        instance.end_partially_suitable = validated_data.get(
            'end_partially_suitable')

        instance.suitable = validated_data.get('suitable', 0)
        instance.end_suitable = validated_data.get('end_suitable', 0)

        instance.save()
        return instance


class ListFilterTestFillInGapSerializer(serializers.Serializer):
    quetion = serializers.CharField()
    answer = serializers.CharField()
    quetion_mark = serializers.IntegerField()
    image = Base64ImageField()


class ListFilterTestOptionSerializer(serializers.Serializer):
    quetion = serializers.CharField()
    option_to_choose_from = serializers.JSONField()
    answer = serializers.CharField()
    quetion_mark = serializers.IntegerField()
    image = Base64ImageField()


class ListFilterTestMultiChoiceQuetionSerializer(serializers.Serializer):
    quetion = serializers.CharField()
    option_to_choose_from = serializers.JSONField()
    answer = serializers.JSONField()
    quetion_mark = serializers.IntegerField()
    image = Base64ImageField()


class CompanyManageJobFTestSerializer(serializers.Serializer):
    title = serializers.CharField()
    fill_in_gap_quetion = ListFilterTestFillInGapSerializer(many=True)
    option_quetion = ListFilterTestOptionSerializer(many=True)
    multi_choice_quetion = ListFilterTestMultiChoiceQuetionSerializer(
        many=True)
    job_test_id = serializers.CharField(read_only=True)

    def bulkCreateFilterQuetionFillInGap(self, data, job_filter_quetionInstance):
        for i in data:
            clean_data = dict(i)
            companyjob_models.TestQuetionFillInGap.objects.create(
                job_test_Quetion=job_filter_quetionInstance,
                quetion=clean_data.get('quetion'),
                answer=clean_data.get('answer'),
                quetion_mark=clean_data.get('quetion_mark'),
                image=clean_data.get("image")

            )

    def bulkCreateFilterOptionQuetion(self, data, job_filter_quetionInstance):
        for i in data:
            clean_data = dict(i)
            companyjob_models.TestQuetionOption.objects.create(
                job_test_quetion=job_filter_quetionInstance,
                quetion=clean_data.get('quetion'),
                anwser=clean_data.get('answer'),
                option_to_choose_from=clean_data.get('option_to_choose_from'),
                quetion_mark=clean_data.get('quetion_mark'),
                image=clean_data.get("image")


            )

    def bulkCreateFilterMultiChoiceQuetion(self, data, job_filter_quetionInstance):
        for i in data:
            clean_data = dict(i)
            companyjob_models.TestQuetionMultiChoiceQuetion.objects.create(
                job_test_quetion=job_filter_quetionInstance,
                quetion=clean_data.get('quetion'),
                anwser=clean_data.get('answer'),
                option_to_choose_from=clean_data.get('option_to_choose_from'),
                quetion_mark=clean_data.get('quetion_mark'),
                image=clean_data.get("image")


            )

    def create(self, validated_data):
        title = validated_data.get('title')
        list_of_fill_in_gap_quetion = validated_data.get(
            'fill_in_gap_quetion', [])
        list_of_option_quetion = validated_data.get('option_quetion', [])
        multi_choice_quetion = validated_data.get('multi_choice_quetion', [])
        company = self.context.get('request').user.companyprofile
        job_filter_quetion = companyjob_models.JobTestQuetion.objects.create(
            title=title, company=company)
        job_filter_quetion.save()

        self.bulkCreateFilterQuetionFillInGap(
            list_of_fill_in_gap_quetion, job_filter_quetion)
        self.bulkCreateFilterOptionQuetion(
            list_of_option_quetion, job_filter_quetion)
        self.bulkCreateFilterMultiChoiceQuetion(
            multi_choice_quetion, job_filter_quetion)

        return {"job_test_id": job_filter_quetion.pk, **validated_data}


class AddTestToJob(serializers.ModelSerializer):

    job_id = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField()

    def create(self, validated_data):
        job_test_quetion_id = validated_data.get('id',)
        job_id = validated_data.get('job_id',)
        job_test_quetion = companyjob_models.JobTestQuetion.objects.get(
            id=job_test_quetion_id)
        job = companyjob_models.Job.objects.get(id=job_id)
        job.job_test = job_test_quetion
        job.save()
        return job

    def validate(self, attrs):
        job_test_quetion_id = attrs.get('id', -1)
        job_id = attrs.get('job_id', -1)
        if not companyjob_models.JobTestQuetion.objects.filter(id=job_test_quetion_id).exists():
            raise CustomValidation(detail='Quetion Does Not exist',
                                   field='id')
        if not companyjob_models.Job.objects.filter(id=job_id).exists():
            raise CustomValidation(detail='Job Does Not exist', field='job_id')
        return super().validate(attrs)

    class Meta:
        model = companyjob_models.JobTestQuetion
        fields = ['id', 'title', 'job_id']


class GenerateJobFinalResultSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()

    def create(self, validated_data):
        job_id = validated_data.get('job_id', -1)
        job = get_object_or_404(companyjob_models.Job, id=job_id,)
        """

            get all CandidateInterviewSheet filtered by interview and applicant
                get the scores calculation save it in JobApplicant.generated_panelist_total_score
        """
        # applicant = companyjob_models.JobApplicant.objects.filter(job=job).first()
        # applicant_base_sheet = []
        # for candidate_sheet in interview_models.CandidateInterviewSheet.objects.filter(interview=job.interview, job_seeker=applicant.jobseekers):
        #     if len(applicant_base_sheet) == 0:
        #         print('Candidtate First')
        #         applicant_base_sheet = candidate_sheet.rating_sheet
        #     else:
        #         print('Candidtate Twice')
        #         count = 1 
        #         while(count <= len(candidate_sheet.rating_sheet) ):
        #             # current_sheet = 
        #             if applicant_base_sheet[count-1].get('value') == candidate_sheet.rating_sheet[count-1].get('value'):
        #                 print('Did the IF')
        #                 applicant_base_sheet[count-1]['score'] = applicant_base_sheet[count-1]['score'] + candidate_sheet.rating_sheet[count-1]['score']
        #                 applicant_base_sheet[count-1]['cut_off'] = applicant_base_sheet[count-1]['cut_off'] + candidate_sheet.rating_sheet[count-1]['cut_off']
                    
        #             count = count +1
        # print({
        #     'applicant_base_sheet':applicant_base_sheet
        # })








        def return_list_of_score(data):
            return data.get('score', 0)
        data = dict()
        for applicant in companyjob_models.JobApplicant.objects.filter(job=job):
            applicantTotalScoreOFAllPanelist = 0
            panelist_count = 0
            for candidate_sheet in interview_models.CandidateInterviewSheet.objects.filter(interview=job.interview, job_seeker=applicant.jobseekers):
                "candidate_sheet represent each review the Panelist created for one jobseeker"
                scoreTotal = sum(
                    map(return_list_of_score, candidate_sheet.rating_sheet))
                panelist_count += 1
                applicantTotalScoreOFAllPanelist += scoreTotal
            if panelist_count == 0:
                applicant.generated_panelist_total_score = 0
            else:
                applicant.generated_panelist_total_score = applicantTotalScoreOFAllPanelist/panelist_count
            applicant.save()

        return data




class JobApplicantDashboardSerializerCleaner(serializers.ModelSerializer):
    jobseekers = serializers.SerializerMethodField()
    cv_id = serializers.SerializerMethodField()
    interview_breakdown = serializers.SerializerMethodField()
    generated_panelist_total_score_current =serializers.SerializerMethodField()

    def get_interview_breakdown(self,applicant:companyjob_models.JobApplicant):
        job_id = applicant.job.id
        job= applicant.job
        applicant_base_sheet = []
        for candidate_sheet in interview_models.CandidateInterviewSheet.objects.filter(interview=job.interview, job_seeker=applicant.jobseekers):
            if len(applicant_base_sheet) == 0:
                applicant_base_sheet = candidate_sheet.rating_sheet
            else:
                count = 1 
                while(count <= len(candidate_sheet.rating_sheet) ):
                    if applicant_base_sheet[count-1].get('value') == candidate_sheet.rating_sheet[count-1].get('value'):
                        print('Did the IF')
                        applicant_base_sheet[count-1]['score'] = applicant_base_sheet[count-1]['score'] + candidate_sheet.rating_sheet[count-1]['score']
                        applicant_base_sheet[count-1]['cut_off'] = applicant_base_sheet[count-1]['cut_off'] + candidate_sheet.rating_sheet[count-1]['cut_off']
                    
                    count = count +1
        return applicant_base_sheet

    def get_generated_panelist_total_score_current(self,applicant:companyjob_models.JobApplicant):
        def return_list_of_score(data):
            return data.get('score', 0)
        data = dict()
        applicantTotalScoreOFAllPanelist = 0
        panelist_count = 0
        for candidate_sheet in interview_models.CandidateInterviewSheet.objects.filter(interview=applicant.job.interview, job_seeker=applicant.jobseekers):
            "candidate_sheet represent each review the Panelist created for one jobseeker"
            scoreTotal = sum( map(return_list_of_score, candidate_sheet.rating_sheet))
            panelist_count += 1
            applicantTotalScoreOFAllPanelist += scoreTotal
        if panelist_count == 0:
            return 0
        else:
            return applicantTotalScoreOFAllPanelist/panelist_count
        
    def get_jobseekers(self, instance: companyjob_models.JobApplicant):
        return {
            'email': instance.jobseekers.user.email,
            'full_name': instance.jobseekers.user.full_name,
            'role_applied_for': instance.job.job_title,
            'date_applied':instance.created_at,
            'id':instance.jobseekers.id
        }

    def get_cv_id(self, instance: companyjob_models.JobApplicant):
        return instance.jobseekers.pk

    class Meta:
        model = companyjob_models.JobApplicant
        fields = '__all__'

        # job_seeker = get_object_or_404(auth_models.)


class ApplicantAndAction(serializers.Serializer):
    applicant_id = serializers.IntegerField()
    action = serializers.CharField()
    letter = serializers.CharField()


class SendFinalLetters(serializers.Serializer):
    "send congrat leeter and other bad news to people"
    list_of_applicant_and_action = ApplicantAndAction(many=True)

    def create(self, validated_data):
        list_of_applicant_and_action = validated_data.get(
            'list_of_applicant_and_action', [])

        for applicant_and_action in list_of_applicant_and_action:
            applicant = get_object_or_404(
                companyjob_models.JobApplicant, id=applicant_and_action.get('applicant_id', -1))
            applicant.final_selection_state = applicant_and_action.get(
                'action', 'idle')
            applicant.acceptance_letter = applicant_and_action.get('letter','<h1>Hello world</h1>')
            applicant.save()
        return list_of_applicant_and_action


class CompanyCandidatesDocsCleaner(serializers.ModelSerializer):

    class Meta:
        model = companyjob_models.JobApplicationDocmentation
        fields = '__all__'


class GetJobTestsSerializer(serializers.Serializer):
    title = serializers.CharField()
    fill_in_gap_quetion = serializers.SerializerMethodField()
    option_quetion = serializers.SerializerMethodField()
    multi_choice_quetion = serializers.SerializerMethodField()
    id = serializers.IntegerField()

    not_suitable = serializers.IntegerField()
    end_not_suitable = serializers.IntegerField()

    partially_suitable = serializers.IntegerField()
    end_partially_suitable = serializers.IntegerField()

    suitable = serializers.IntegerField()
    end_suitable = serializers.IntegerField()

    def get_fill_in_gap_quetion(self, instance):
        all_fill_gap_questions = companyjob_models.TestQuetionFillInGap.objects.filter(
            job_test_Quetion=instance)
        list_of_questions = []

        for i in all_fill_gap_questions:
            list_of_questions.append(
                {"id": i.id, "quetion": i.quetion, "answer": i.answer, "image": "" if not i.image else i.image.url, "quetion_mark": i.quetion_mark})
        return list_of_questions

    def get_option_quetion(self, instance):
        all_option_quetion = companyjob_models.TestQuetionOption.objects.filter(
            job_test_quetion=instance)
        list_of_questions = []

        for i in all_option_quetion:
            list_of_questions.append(
                {"id": i.id, "quetion": i.quetion, "option_to_choose_from": i.option_to_choose_from, "answer": i.anwser, "image": "" if not i.image else i.image.url, "quetion_mark": i.quetion_mark})
        return list_of_questions

    def get_multi_choice_quetion(self, instance):
        all_multi_choice_quetion = companyjob_models.TestQuetionMultiChoiceQuetion.objects.filter(
            job_test_quetion=instance)
        list_of_questions = []

        for i in all_multi_choice_quetion:
            list_of_questions.append(
                {"id": i.id, "quetion": i.quetion, "answer": i.answer, "image": "" if not i.image else i.image.url, "quetion_mark": i.quetion_mark})
        return list_of_questions


class InvitationLetterSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(
        allow_null=False, required=True, queryset=companyjob_models.Job.objects.all())
    letter_content = serializers.CharField(required=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, attrs):
        job: companyjob_models.Job = attrs.get("job", "")
        if not job:
            raise CustomValidation(
                field="job", detail="Invalid field", status_code=status.HTTP_400_BAD_REQUEST)

        if self.context.get('request').user.companyprofile != job.company:
            raise CustomValidation(
                field="job", detail="Unauthorized request", status_code=status.HTTP_401_UNAUTHORIZED)

        return attrs

    class Meta:
        model = companyjob_models.JobInvitationLetter
        fields = ["id", "job", "company", "letter_content"]


class GetJobFiltersSerializer(serializers.Serializer):
    title = serializers.CharField()
    fill_in_gap_quetion = serializers.SerializerMethodField()
    option_quetion = serializers.SerializerMethodField()
    multi_choice_quetion = serializers.SerializerMethodField()
    id = serializers.IntegerField()

    not_suitable = serializers.IntegerField()
    end_not_suitable = serializers.IntegerField()

    partially_suitable = serializers.IntegerField()
    end_partially_suitable = serializers.IntegerField()

    suitable = serializers.IntegerField()
    end_suitable = serializers.IntegerField()

    def get_fill_in_gap_quetion(self, instance):
        all_fill_gap_questions = companyjob_models.FilterQuetionFillInGap.objects.filter(
            job_filter_quetion=instance)
        list_of_questions = []

        for i in all_fill_gap_questions:
            list_of_questions.append(
                {"id": i.id, "quetion": i.quetion, "answer": i.answer, "image": "" if not i.image else i.image.url, "quetion_mark": i.quetion_mark})
        return list_of_questions

    def get_option_quetion(self, instance):
        all_option_quetion = companyjob_models.FilterQuetionOption.objects.filter(
            job_filter_quetion=instance)
        list_of_questions = []

        for i in all_option_quetion:
            list_of_questions.append(
                {"id": i.id, "quetion": i.quetion, "option_to_choose_from": i.option_to_choose_from, "answer": i.anwser, "image": "" if not i.image else i.image.url, "quetion_mark": i.quetion_mark})
        return list_of_questions

    def get_multi_choice_quetion(self, instance):
        all_multi_choice_quetion = companyjob_models.FilterQuetionMultiChoiceQuetion.objects.filter(
            job_filter_quetion=instance)
        list_of_questions = []

        for i in all_multi_choice_quetion:
            list_of_questions.append(
                {"id": i.id, "quetion": i.quetion, "answer": i.answer, "image": "" if not i.image else i.image.url, "quetion_mark": i.quetion_mark})
        return list_of_questions


class GetCVDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.JobSeekerProfile
        fields = "__all__"
