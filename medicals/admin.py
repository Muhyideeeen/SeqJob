from django.contrib import admin
from . import models
# Register your models here.


admin.site.register(models.JobMedicals)
admin.site.register(models.TrackCandidateJobMedicalsInvitation)
admin.site.register(models.UploadedMedicalReport)