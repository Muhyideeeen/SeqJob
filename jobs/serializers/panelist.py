from rest_framework import serializers
from jobs import models as companyjob_models

class PanelistJobCleanerSerializer(serializers.ModelSerializer):

    interview = serializers.SerializerMethodField()
    org_name = serializers.SerializerMethodField()

    def get_org_name(self,job):
        return job.company.organisation_name

    def get_interview(self,job:companyjob_models.Job):
        return job.interview.id
    
    class Meta:
        model  = companyjob_models.Job
        fields  = [
        'job_title','is_active','location',
        'job_type','salary','currency','job_required_document',
        'description','job_filter','interview',
        'description_content','id','country','org_name'
        ]
