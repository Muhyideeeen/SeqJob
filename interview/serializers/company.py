from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from jobs.models import Job, JobApplicant
from utils.exception import CustomValidation
from .. import models
from myauthentication import models as auth_models
import json
from interview.models import Interview, TrackCandidateInterviewInvitation
from myauthentication.permissions import JobMustHaveTestOrQuetionSetBeforeInterviewPermissions


class RatingSheet(serializers.Serializer):
    name = serializers.CharField()
    cut_off = serializers.IntegerField()


class ListOfEmail(serializers.Serializer):
    email = serializers.EmailField()


class ListOfAvailableDates(serializers.Serializer):
    available_dates = serializers.DateField()


class ListOfAvailableTime(serializers.Serializer):
    available_time = serializers.TimeField()


class CompanySetUpInterview(serializers.Serializer):
    job_id = serializers.IntegerField()
    list_of_available_dates = ListOfAvailableDates(many=True)
    list_of_available_time = ListOfAvailableTime(many=True)
    rating_sheet = RatingSheet(many=True)
    list_of_email = ListOfEmail(many=True)
    interview_link = serializers.CharField(required=False)
    panelist_invitation_letter = serializers.CharField()

    def _validate_job_is_for_company(self, attrs):
        job: Job = get_object_or_404(Job, id=attrs.get('job_id', -1))

        # let check if job has interview
        check_if_job_has_intervew: bool = False
        try:
            job.interview
            check_if_job_has_intervew = True
        except:
            check_if_job_has_intervew = False

        if check_if_job_has_intervew:
            raise CustomValidation('Already has a interview', field='job_id')
        else:
            current_logged_in_company = self.context.get(
                'request').user.companyprofile
            if current_logged_in_company.id != job.company.id:
                raise CustomValidation(
                    detail='unauthorized', field='job_id', status_code=status.HTTP_401_UNAUTHORIZED)

            list_of_email = attrs.get('list_of_email')
            errors = []
            for email in list_of_email:
                email = email.get('email')
                current_user = auth_models.User.objects.filter(email=email)
                if current_user.exists():
                    current_user = current_user.first()
                    'if he exist check if he is a pannelist'
                    if current_user.user_type == 'panelist':
                        pass
                        # if current_user.panelistprofile.company.id != current_logged_in_company.id:
                        #     errors.append(f'{email} already exist as a pannelist in another organisation')
                    else:
                        errors.append(
                            f'{email} already exists as a {current_user.user_type}')

            if len(errors) != 0:
                raise CustomValidation(errors, field='list_of_email')

    def create(self, validated_data):
        self._validate_job_is_for_company(validated_data)
        interview_link = validated_data.get('interview_link', 'pending')
        list_of_available_dates = validated_data.get('list_of_available_dates')
        list_of_available_time = validated_data.get('list_of_available_time')
        rating_sheet = validated_data.get('rating_sheet')
        list_of_email = validated_data.get('list_of_email')
        job: Job = get_object_or_404(Job, id=validated_data.get('job_id'))
        letter = validated_data.get('panelist_invitation_letter')
        # permmit =
        interview = models.Interview.objects.create(
            company=self.context.get('request').user.companyprofile,
            job=job,
            list_of_available_dates=json.dumps(
                list_of_available_dates, default=str),
            list_of_available_time=json.dumps(
                list_of_available_time, default=str),
            rating_sheet=rating_sheet,
            list_of_email=list_of_email,
            interview_link=interview_link,
            panelist_invitation_letter=letter
        )

        return interview

    def update(self, instance: models.Interview, validated_data):

        job: Job = get_object_or_404(Job, id=validated_data.get('job_id'))
        interview = Interview.objects.get(job=job)
        interview.interview_link = validated_data.get(
            'interview_link', interview.interview_link)
        interview.rating_sheet = validated_data.get(
            'rating_sheet', interview.rating_sheet)
        interview.list_of_email = validated_data.get(
            'list_of_email', interview.list_of_email)
        interview.panelist_invitation_letter = validated_data.get(
            'panelist_invitation_letter', interview.panelist_invitation_letter)
        list_of_available_dates = validated_data.get(
            'list_of_available_dates', None)
        list_of_available_time = validated_data.get(
            'list_of_available_time', None)
        if list_of_available_dates:
            interview.list_of_available_dates = json.dumps(
                list_of_available_dates+interview.list_of_available_dates)
        if list_of_available_time:
            interview.list_of_available_time = json.dumps(
                list_of_available_time+interview.list_of_available_time)
        interview.save()

        # interview.lis
        # print('hell world',{'instance':instance,
        #                     'validated_data':validated_data})
        return interview


class InterviewCleaner(serializers.ModelSerializer):
    list_of_available_time = serializers.SerializerMethodField()
    list_of_available_dates = serializers.SerializerMethodField()

    def get_list_of_available_dates(self, instance: Interview):
        data = json.loads(instance.list_of_available_dates)
        return data

    def get_list_of_available_time(self, instance: Interview):
        data = json.loads(instance.list_of_available_time)
        return data

    class Meta:
        model = Interview
        fields = '__all__'


class TrackCandidateInterviewInvitationCleaner(serializers.ModelSerializer):
    job_seeker = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    candidates_applied = serializers.SerializerMethodField()
    job_applicant_id = serializers.SerializerMethodField()

    def get_job_applicant_id(self,instance:TrackCandidateInterviewInvitation):
        applicant = JobApplicant.objects.filter(jobseekers=instance.job_seeker,job=instance.interview.job)
        return applicant.first().id

    def get_job(self, instance: TrackCandidateInterviewInvitation):
        return {
            'company_name': instance.interview.company.organisation_name,
            'position': instance.interview.job.job_title,
        }

    def get_candidates_applied(self, instance: TrackCandidateInterviewInvitation):
        return JobApplicant.objects.filter(job=instance.interview.job).count()

    def get_job_seeker(self, instance: TrackCandidateInterviewInvitation):
        cv = ''
        try:
            cv = instance.job_seeker.cv.url
        except:
            cv = ''
        return {
            'full_name': instance.job_seeker.user.full_name,
            'email': instance.job_seeker.user.email,
            'cv': cv,
            'id':instance.job_seeker.id
        }

    class Meta:
        model = TrackCandidateInterviewInvitation
        fields = ['id', 'interview', 'date_picked', 'time_picked', 'has_mail_sent',
                  'has_picked_invitation', 'job_seeker', 'candidates_applied', 'job','job_applicant_id']
