from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter


route = DefaultRouter()

route.register('users-settings',views.UserSettings,basename='users-settings')
route.register('admin-setstuff',views.AdminManagerUserPassword,basename='admin-setstuff')
route.register('forgot-password',views.ForgotPasswordViewSet,basename='forgot-password')

urlpatterns= [
    path('create-company/',views.RegisterCompanyView.as_view(),name='create-company'),
    path('create-seeker/',views.RegisterJobSeekerView.as_view(),name='create-seeker'),
    path('create-hr/',views.RegisterHrView.as_view(),name='create-hr'),
    path('login/',views.Login.as_view(),name='login'),
    path('company-profile/',views.CompanyProfileApi.as_view()),
    path('jobseeker-profile/',views.JobSeekerProfileApi.as_view()),
    path('panelist-profile/',views.PanelistProfileApi.as_view()),
    path('parse-cv-file/',views.parse_cv_file)
] + route.urls