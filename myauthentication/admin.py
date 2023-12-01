from django.contrib import admin
from .models import MedicalRepProfile, User,CompanyProfile,JobSeekerProfile,HrProfile,PanelistProfile
from jobs.models import JobApplicant
# Register your models here.


admin.site.register(User)
admin.site.register(HrProfile)
admin.site.register(JobSeekerProfile)
admin.site.register(CompanyProfile)
admin.site.register(JobApplicant)
admin.site.register(PanelistProfile)
admin.site.register(MedicalRepProfile)