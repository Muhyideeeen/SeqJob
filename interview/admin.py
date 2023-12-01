from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Interview)
admin.site.register(models.CandidateInterviewSheet)
admin.site.register(models.TrackCandidateInterviewInvitation)