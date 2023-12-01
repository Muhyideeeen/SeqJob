
from rest_framework.routers import DefaultRouter
from .views.company import CompanySetUpMedicals
from .views.job_seekers import JobSeekerManageMedicals

router = DefaultRouter()
router.register('medic_setup',CompanySetUpMedicals,basename='medic_setup')
router.register('job_seeker_manage_medic',JobSeekerManageMedicals,basename='JobSeekerManageMedicals')


urlpatterns = [
    
] + router.urls