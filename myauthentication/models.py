from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from rest_framework import status
from utils.exception  import  CustomValidation
from cloudinary_storage.storage import RawMediaCloudinaryStorage
# from django.apps import apps
# Create your models here.
# User
USER_TYPES = ['company','job_seakers','hr','admin','panelist','medic']
# JOB_MODEL = apps.get_model(app_label='jobs',model_name='Job',)
class UserManager(BaseUserManager):


    def create_user(self, email, user_type:str, password=None):
        'create a user'

        if password is None:
            raise CustomValidation(detail='Password Is required',field='password',status_code=status.HTTP_400_BAD_REQUEST)
        
        if not user_type in USER_TYPES:
            'it the user_type does not exist in the list'
            raise CustomValidation(detail='USER TYPES MUST BE '+str(USER_TYPES),field='user_type',status_code=status.HTTP_400_BAD_REQUEST)


        user = self.model(
            email=self.normalize_email(email.lower()),
            user_type= user_type)
        user.set_password(password)
        user.save()
        return user

    def create_medic(self,email,job=None,company=None,password=None):
        'medic creation helper'
        if job is None or company is None:
            raise CustomValidation('Job or Compant fields cant be empty',field='medic_creation')
        user =  self.create_user(
                        email=email,
            password=password,
            user_type = 'medic'
        )
        medic= MedicalRepProfile.objects.create(
            user=user
        )
        medic.company.add(company)
        medic.job.add(job)
        medic.save()
        return medic

    def create_panelist(self,email,job=None,company=None,password=None):
        "panelist creation helper"
        if job is None or company is None:
            raise CustomValidation('Job or company fields cant be empty',field='panelist_creation')
        user = self.create_user(
            email=email,
            password=password,
            user_type = 'panelist'
        )
        panelist = PanelistProfile.objects.create(
            user=user,
            # job=job,
            # company=company
        )
        panelist.company.add(company)
        panelist.job.add(job)
        panelist.save()
        return panelist


    def create_superuser(self, email, password=None):
        'Creates and saves a superuser'
        user = self.create_user(
            email=email,
            password=password,
            user_type = 'admin'
        )
        user.is_staff=True
        user.is_admin=True
        user.is_superuser=True
        user.is_active=True
        user.save(using=self._db)
        return user
    def create_company(self,email,password):
        user = self.create_user(
            email=email,
            password=password,
            user_type = 'company'
        )

        return user

    
    def create_joobseeker(self,email,password,phone_number):
        'this create a job seeker'
        user = self.create_user(
            email=email,
            password=password,
            user_type='job_seakers'
        )
        job_seeker = JobSeekerProfile.objects.create(
            user=user
        )
        return job_seeker
        
class User(AbstractBaseUser,PermissionsMixin):
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name= models.TextField()
    class UserChoices(models.TextChoices):
        company='company'
        job_seakers='job_seakers'
        hr='hr'
        admin='admin'
        panelist='panelist'
        medic='medic'
    user_type = models.CharField(max_length=25,choices=UserChoices.choices)
    profile_image = models.ImageField(upload_to='profile_image/%d/',blank=True,null=True,default=None)
    phone_number = models.CharField(max_length=15)


    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS  = ['user_type']

    objects = UserManager()
    def __str__(self):
        return self.email


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    cv  = models.FileField(upload_to='job_seeker_cv/%d/%m'
    ,null=True,default=None,
        storage=RawMediaCloudinaryStorage(),
    )
    notify_me_on = models.TextField(default='',blank=True)
    first_name = models.CharField(max_length=500,default=' ',)
    middle_name = models.CharField(max_length=500,default=' ',)
    last_name = models.CharField(max_length=500,default=' ',)
    phone_number = models.CharField(max_length=500,default=' ',)
    email = models.CharField(max_length=500,default=' ',)
    addresse = models.CharField(max_length=500,default=' ',)
    city = models.CharField(max_length=500,default=' ',)
    state = models.CharField(max_length=500,default=' ',)
    country_of_residence = models.CharField(max_length=500,default=' ',)
    linkdin = models.TextField(blank=True,null=True,default='Null',)
    twitter = models.TextField(blank=True,null=True,default='Null')
    personal_statement = models.TextField(default='I am Good')
    """
    education{
    degree_type:'hnd',
    school_name:djdj,
    start_year:'fke',
    end_year:'dhiud',
    course_of_study:'ddfe',
    }"""
    education = models.JSONField(default=list)
    """
    experience{
    Company:...,
    Start Year:...,
    End Year:...,
    role:...,
    Responsibilities:...,
    }"""
    experience = models.JSONField(default=list)

    """
    Certificaton{
    Certification,
    Start Year
    Issuer
    }"""
    certificaton = models.JSONField(default=list)

    """
    Refrences{
    Full Name;
    Relationship;
    Email;
    Phone Number;
    }
    """
    refrences = models.JSONField(default=list)
    has_updated_cv= models.BooleanField(default=False)
class CompanyProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    organisation_name = models.CharField(max_length=200)
    organisation_name_shortname = models.CharField(max_length=100,unique=True,default=f'short')
    industry  = models.CharField(max_length=100)
    organisation_size  = models.IntegerField(default=0)
    location  = models.TextField()
    # on save we make the email the official mail
    official_mail = models.EmailField(null=True,default=None)
    addresses = models.TextField()
    official_phone = models.CharField(max_length=15)


class HrProfile(models.Model):
    user  = models.OneToOneField(User,on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyProfile,on_delete=models.CASCADE)#when a company is deleted delete all hr that has to do with him


class PanelistProfile(models.Model):
    'this is someone that rate a interview he get deleted when a job is deleted '
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    job = models.ManyToManyField('jobs.Job')
    company = models.ManyToManyField(CompanyProfile,)



class MedicalRepProfile(models.Model):
    'this is someone that rate a interview he get deleted when a job is deleted '
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    job = models.ManyToManyField('jobs.Job')
    company = models.ManyToManyField(CompanyProfile,)
    hospital_name = models.TextField()
    hospital_phone = models.CharField(max_length=12,blank=True,null=True,default=True)
    hospital_email = models.EmailField(max_length=12,blank=True,null=True,default=True)