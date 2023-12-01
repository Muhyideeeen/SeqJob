from rest_framework import serializers
from .. import models as interview_models
from jobs import models as job_models
from django.shortcuts import get_object_or_404

class  RatingSheet(serializers.Serializer):
    """
    #we getting this info from a get request we fetch from Interview db 
        score is where the panelist comes in 
        cut_off has been set by Company
    """
    value = serializers.CharField()
    score = serializers.IntegerField()
    cut_off = serializers.IntegerField()

class PanelistRateJobSeekeers(serializers.Serializer):
    job = serializers.IntegerField()
    job_applicant = serializers.IntegerField()
    rating_sheet = RatingSheet(many=True)
    interviewer_remark = serializers.CharField()
    summary_of_qualification = serializers.CharField()

    def create(self, validated_data):
        job_id = validated_data.get('job',)
        job_applicant_id =validated_data.get('job_applicant',)
        panelist = self.context.get('request').user.panelistprofile
        job = get_object_or_404(job_models.Job,id=job_id)


        job_applicant = get_object_or_404(job_models.JobApplicant,id=job_applicant_id)

        sheet,_ = interview_models.CandidateInterviewSheet.objects.get_or_create(
            interview = job.interview,
            job_seeker = job_applicant.jobseekers,
            panelist=panelist
        )
        sheet.rating_sheet = validated_data.get('rating_sheet','...')
        sheet.interviewer_remark = validated_data.get('interviewer_remark','..')
        sheet.summary_of_qualification = validated_data.get('summary_of_qualification','...')

        sheet.save()
        return sheet

class CandidateInterviewSheetCleanerSerializer(serializers.ModelSerializer):

    class Meta:
        model  =interview_models.CandidateInterviewSheet
        fields = [ 'interview','job_seeker','panelist','rating_sheet','interviewer_remark','summary_of_qualification','id']


class PanelistAggregateCleaner(serializers.ModelSerializer):
    panelist = serializers.SerializerMethodField()


    def get_panelist(self,instance:interview_models.CandidateInterviewSheet):

        return {
            'name':instance.panelist.user.full_name,
            'id':instance.panelist.id,
            'email':instance.panelist.user.email
        }
    class Meta:
        model = interview_models.CandidateInterviewSheet
        fields = [
            'panelist',
            'rating_sheet',
            'summary_of_qualification',
            'interviewer_remark'
        ]