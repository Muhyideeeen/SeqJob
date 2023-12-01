from rest_framework.routers import DefaultRouter
from .views import company as company_related_views
from .views import panelist as panelist_related_views
from .views import job_seekers as job_seekers_related_views

route =  DefaultRouter()

route.register('interview_setup',company_related_views.CompanySetUpInterView,basename='interview_setup')
route.register('panelist_view_jobs',panelist_related_views.PanelistHandlesInterview,basename='panelist_view_jobs')
route.register('job_seeker_manage_invites',job_seekers_related_views.JobSeekersManageInterviewViewSet,basename='job_seeker_manage_invites')


urlpatterns = [

] + route.urls