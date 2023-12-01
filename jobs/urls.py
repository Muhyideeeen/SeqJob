from rest_framework.routers import DefaultRouter
from jobs.views import company as company_job_views
from jobs.views import general as general_job_views
from jobs.views import job_seeker as job_seeker_job_views
from django.urls import path
route = DefaultRouter()

route.register('company-job-handler',
               company_job_views.CompanyManageJobs, basename='company-job-hanler')
route.register('company-filterquetion-handler',
               company_job_views.CompanyManageQuetions, basename='company-filterquetion-handler')
route.register('company-test-handler',
               company_job_views.CompanyManageTest, basename='company-test-handler')
route.register('company-generate-job-final-result',
               company_job_views.GenerateJobFinalResult, basename='GenerateJobFinalResult')
route.register('general-quetion-view',
               general_job_views.QuetionViewset, basename='general-quetion')

route.register('job-seeker-view',
               job_seeker_job_views.JobSeekersApply, basename='job-seeker-view')
route.register('jobseeker-application-process',
               job_seeker_job_views.JobSeekerApplicationViewSet, basename='jobSeeker_application_process')
route.register('cv_upload', job_seeker_job_views.UploadCvViewSet)
route.register('job-seeker-dashboard',
               job_seeker_job_views.JobSeekerDashboard, basename='job-seeker-dashboard')
route.register('job-seeker-handles-doc',
               job_seeker_job_views.JobSeekerHandleDocs, basename='job-seeker-handles-doc')
urlpatterns = [
    path("company-test-handler/invitation-letter", company_job_views.JobInvitationLetterView.as_view(),
         name="invitation-letter"),
    path("company-test-handler/invitation-letter/<int:id>",
         company_job_views.JobInvitationLetterDetailView.as_view(), name="invitation-letter-detail"),
    path("company-test-handler/find-jobs-inivitation-letter/<int:jobId>",
         company_job_views.FindJobsInvitationView.as_view(), name="find-jobs-inivitation-letter"),
    path("company-job-handler/cv-details/<int:id>", company_job_views.GetCVDetailsView.as_view(),
         name="company-job-handler/cv-details"),
    path("company-job-handler/cv-details/all", company_job_views.GetAllCompanyRelatedCVsView.as_view(),
         name="company-job-handler/cv-details/all")
] + route.urls
