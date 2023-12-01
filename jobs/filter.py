import django_filters
from . import models



class JobFIlter(django_filters.FilterSet):

    job_title = django_filters.CharFilter(field_name='job_title',lookup_expr='icontains')

    class Meta:
        fields = ['is_active','job_title','job_type']
        model = models.Job


class JobApplicantFilter(django_filters.FilterSet):

    class Meta:
        fields = ['final_selection_state']
        model = models.JobApplicant
