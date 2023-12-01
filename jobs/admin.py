from django.contrib import admin
from . import models
# Register your models here.


admin.site.register(models.Job)

admin.site.register(models.JobApplicationDocmentation)

admin.site.register(models.JobInvitationLetter)


class FilterQuetionFillInGapAdmin(admin.TabularInline):
    model = models.FilterQuetionFillInGap
    extra: int = 1


class FilterQuetionOptionAdmin(admin.TabularInline):
    model = models.FilterQuetionOption
    extra: int = 1


class FilterQuetionMultiChoiceAdmin(admin.TabularInline):
    model = models.FilterQuetionMultiChoiceQuetion
    extra: int = 1


class JobFilterQuetionAdmin(admin.ModelAdmin):
    inlines = [FilterQuetionFillInGapAdmin, FilterQuetionOptionAdmin,
               FilterQuetionMultiChoiceAdmin]


admin.site.register(
    models.JobFilterQuetion, JobFilterQuetionAdmin
)


class TestFillInGapAdmin(admin.TabularInline):
    model = models.TestQuetionFillInGap
    extra: int = 1


class TestOptionAdmin(admin.TabularInline):
    model = models.TestQuetionOption
    extra: int = 1


class TestMultiChoiceAdmin(admin.TabularInline):
    model = models.TestQuetionMultiChoiceQuetion
    extra: int = 1


class JobTestAdmin(admin.ModelAdmin):
    inlines = [TestFillInGapAdmin, TestOptionAdmin,
               TestMultiChoiceAdmin]


admin.site.register(
    models.JobTestQuetion, JobTestAdmin
)
