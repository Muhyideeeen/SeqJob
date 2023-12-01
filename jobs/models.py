from django.db import models
from myauthentication import models as auth_models
from cloudinary_storage.storage import RawMediaCloudinaryStorage
import collections
from django.utils.translation import gettext_lazy as _
# Create your models here.exit


class JobTestQuetion(models.Model):
    'this test is to check the applicant knowledge For the Job'
    title = models.TextField()
    company = models.ForeignKey(
        auth_models.CompanyProfile, null=True, default=True, on_delete=models.CASCADE,)
    "Depening on this mark here that what we will uuse to filter the suiteable from the not suitable"
    suitable = models.IntegerField(default=21)
    end_suitable = models.IntegerField(default=100)

    partially_suitable = models.IntegerField(default=11)
    end_partially_suitable = models.IntegerField(default=20)

    not_suitable = models.IntegerField(default=0)
    end_not_suitable = models.IntegerField(default=10)


class TestQuetionFillInGap(models.Model):
    job_test_Quetion = models.ForeignKey(
        JobTestQuetion, on_delete=models.CASCADE)
    quetion = models.TextField()
    answer = models.TextField()
    image = models.ImageField(
        upload_to='testquestion/%d/', default=None, blank=True, null=True)
    quetion_mark = models.IntegerField(default=1)

    def mark_question(self, user_answer):
        return self.answer == user_answer


class TestQuetionOption(models.Model):
    job_test_quetion = models.ForeignKey(
        JobTestQuetion, on_delete=models.CASCADE)
    quetion = models.TextField()
    option_to_choose_from = models.JSONField()
    anwser = models.CharField(max_length=300)
    image = models.ImageField(
        upload_to='testquestion/%d/', default=None, blank=True, null=True)
    quetion_mark = models.IntegerField(default=1)

    def mark_question(self, user_answer):
        return self.anwser == user_answer


class TestQuetionMultiChoiceQuetion(models.Model):
    job_test_quetion = models.ForeignKey(
        JobTestQuetion, on_delete=models.CASCADE)
    quetion = models.TextField()
    option_to_choose_from = models.JSONField()
    anwser = models.JSONField()
    image = models.ImageField(
        upload_to='testquestion/%d/', default=None, blank=True, null=True)
    quetion_mark = models.IntegerField(default=1)

    def mark_question(self, user_answer):
        return collections.Counter(self.anwser) == collections.Counter(user_answer)


class JobFilterQuetion(models.Model):
    'this is Test is to filter cv only'
    title = models.TextField()
    company = models.ForeignKey(
        auth_models.CompanyProfile, null=True, default=True, on_delete=models.CASCADE,)
    "Depening on this mark here that what we will uuse to filter the suiteable from the not suitable"
    suitable = models.IntegerField(default=20)
    end_suitable = models.IntegerField(default=100)

    partially_suitable = models.IntegerField(default=11)
    end_partially_suitable = models.IntegerField(default=20)

    not_suitable = models.IntegerField(default=0)
    end_not_suitable = models.IntegerField(default=10)


class FilterQuetionFillInGap(models.Model):
    job_filter_quetion = models.ForeignKey(
        JobFilterQuetion, on_delete=models.CASCADE)
    quetion = models.TextField()
    answer = models.TextField()
    image = models.ImageField(
        upload_to='filterquestion/%d/', default=None, blank=True, null=True)
    quetion_mark = models.IntegerField(default=1)

    def mark_question(self, user_answer):
        return self.answer == user_answer


class FilterQuetionOption(models.Model):
    job_filter_quetion = models.ForeignKey(
        JobFilterQuetion, on_delete=models.CASCADE)
    quetion = models.TextField()
    option_to_choose_from = models.JSONField()
    anwser = models.CharField(max_length=300)
    image = models.ImageField(
        upload_to='filterquestion/%d/', default=None, blank=True, null=True)
    quetion_mark = models.IntegerField(default=1)

    def mark_question(self, user_answer):
        return self.anwser == user_answer


class FilterQuetionMultiChoiceQuetion(models.Model):
    job_filter_quetion = models.ForeignKey(
        JobFilterQuetion, on_delete=models.CASCADE)
    quetion = models.TextField()
    option_to_choose_from = models.JSONField()
    anwser = models.JSONField()
    image = models.ImageField(
        upload_to='filterquestion/%d/', default=None, blank=True, null=True)
    quetion_mark = models.IntegerField(default=1)

    def mark_question(self, user_answer):
        return collections.Counter(self.anwser) == collections.Counter(user_answer)


class Job(models.Model):
    "One Company can have plenty jobs listed"
    job_title = models.CharField(max_length=250)
    is_active = models.BooleanField(default=False)
    location = models.TextField()
    country = models.TextField(default='')
    company = models.ForeignKey(
        auth_models.CompanyProfile, on_delete=models.CASCADE, null=True, default=None)
    # newly added fields by elijah

    class employment_type_choice(models.TextChoices):
        full_time = "full_time"
        part_time = "part_time"
        contract = "contract"

    employement_type = models.CharField(
        max_length=30, choices=employment_type_choice.choices)
    money_sign = models.CharField(max_length=5)
    required_experience = models.CharField(max_length=255)
    generic_skills = models.CharField(max_length=255)
    technical_skills = models.CharField(max_length=255)
    professional_path = models.CharField(max_length=255)
    # newly added fields by elijah

    class job_type_choice(models.TextChoices):
        hybrid = 'hybrid'
        on_site = 'on_site'
        remote = 'remote'
    job_type = models.CharField(max_length=10, choices=job_type_choice.choices)
    salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    currency = models.CharField(max_length=20, default='naira')
    number_of_applicant = models.IntegerField(default=0)
    # this will be seprated by comma so we can create a list out of the names
    job_required_document = models.TextField(default='')

    # required_experience
    description = models.FileField(upload_to='jobdescription/%d/%m', null=True, default=None,
                                   storage=RawMediaCloudinaryStorage(),
                                   )
    description_content = models.TextField(default='',)

    class JobVariantChoices(models.TextChoices):
        filter_only = 'filter_only', _('filter_only')
        filter_and_test = 'filter_and_test', _('filter_and_test')

    job_variant = models.CharField(max_length=30,
                                   choices=JobVariantChoices.choices, default=JobVariantChoices.filter_only)
    job_filter = models.ForeignKey(
        JobFilterQuetion, on_delete=models.SET_NULL, null=True, default=None)
    # this is optional if the job variant does not need it
    job_test = models.ForeignKey(
        JobTestQuetion, on_delete=models.SET_NULL, null=True, default=None)

    quetion_overall_mark = models.IntegerField(default=100)
    '''
        Physician assistant and Nurse practitioner can be a category but here it will be seprated by comma e.g "Physician assistant,Nurse practitioner"
    the idea is the job owner picks all the job categories u likes from the option that would be sent to the front end
    the job seeker would have pick what he wants to be notified on so once this is created if it exist in what the job seekers selected he would be notified
    '''
    job_categories = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            return f'{self.job_title} by ({self.company.organisation_name_shortname})'
        except:
            return f'{self.job_title}'

    def validate_job_required_document(self, keys):
        print({
            'splited': collections.Counter(self.job_required_document.split(',')),
            'keys': keys,
            'database': self.job_required_document.split(',')
        })
        return collections.Counter(self.job_required_document.split(',')) == collections.Counter(keys)


class JobInvitationLetter(models.Model):
    company = models.ForeignKey(
        to=auth_models.CompanyProfile, on_delete=models.CASCADE)
    job = models.OneToOneField(to=Job, on_delete=models.CASCADE)
    letter_content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobApplicant(models.Model):
    jobseekers = models.ForeignKey(
        auth_models.JobSeekerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    filter_quetions_score = models.IntegerField(default=0)
    test_quetions_score = models.IntegerField(default=0)
    "this boolean is for the filter quetioon"
    has_written_exam = models.BooleanField(default=False)
    "this boolean is for the Test quetioon"
    has_written_test = models.BooleanField(default=False)
    has_mail_sent = models.BooleanField(default=False)
    generated_panelist_total_score = models.IntegerField(default=0)
    has_been_invited_for_medicals = models.BooleanField(default=False)
    'this letter will be sent to thier email (it more of an acceptance letter)'
    acceptance_letter = models.TextField(default='<h1>Hello world</h1>')

    class FinalSelectionStateChoices(models.TextChoices):
        """
        selected - this are the  people we are sending good news too
        in_view = we did not select u but we are going to reach out to u in the feature
        not_selected = bad news
        idle = defualt is idle meaning no actiion for this lot yet

        Note if the person alread have this status there is no need to send again to avoid duplicate
        """
        selected = 'selected'
        in_view = 'in_view'
        not_selected = 'not_selected'
        idle = 'idle'
    final_selection_state = models.CharField(
        max_length=20, choices=FinalSelectionStateChoices.choices, default=FinalSelectionStateChoices.idle)
    has_sent_selection_mail = models.BooleanField(default=False)

    # can be changed if FinalSelectionStateChoices is == selected
    accept_application = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobApplicationDocmentation(models.Model):
    job_applicant = models.ForeignKey(JobApplicant, on_delete=models.CASCADE)
    name_of_file = models.TextField()
    file = models.FileField(upload_to='job_application_docs', null=True, default=None,
                            storage=RawMediaCloudinaryStorage(),)
