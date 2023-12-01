from time import sleep
from .EmailConfirmation import activateEmail,activatePanelistEmail,invitePanelist,invite_job_seeker,send_application_letters
from celery import shared_task
from django.contrib.auth import get_user_model
from jobs import models as job_models
from mailing.EmailConfirmation import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from .tokens import account_activation_token

import os
@shared_task()
def send_activation_mail(user_id,to_email):
    user = get_user_model().objects.get(id=user_id)
    activateEmail(user,to_email)



@shared_task()
def handle_activatePanelistEmail(user_id,to_email,password):
    user = get_user_model().objects.get(id=user_id)
    user.is_active=True
    user.save()

    activatePanelistEmail(user,to_email,password)


@shared_task()
def handle_invitePanelist(user_id,to_email,companyName,job_id=None,letter='hello'):
    user = get_user_model().objects.get(id=user_id)
    job_name = None
    if job_id is not None:
        job  = job_models.Job.objects.get(id=job_id)
        job_name= job.job_title

    mail_subject = f'You Have Been Invited as panelist for {companyName}'
    job_title = ''
    if job_name is not None:
        job_title = job_name
    data  = {
        user:user,
        'domain':os.environ['domain'],
        'companyName':companyName,
        'full_name':user.full_name,
        'job_title':job_title,
        'letter':letter
    }
    message = render_to_string('panelist_invite.html',context=data)

    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":to_email,"name":"rel8"}])

    # invitePanelist(user,to_email,companyName,job_name)


@shared_task()
def handle_activateMedicEmail(user_id,to_email,password):
    user = get_user_model().objects.get(id=user_id)
    user.is_active=True
    user.save()
    mail_subject = 'You have been invited as a medic on Squential Job'
    data = {
        user:user,
        'domain':os.environ['domain'],
        'uid':urlsafe_base64_encode(force_bytes(user.id)),
        'token':account_activation_token.make_token(user=user),
        'password':password
        # 'protocol':'https'
    }
    message = render_to_string('medic_activate.html',context=data)
    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":to_email,"name":"rel8"}])
@shared_task()
def handle_inviteMedicalRep(user_id,to_email,companyName,job_id=None):
    user = get_user_model().objects.get(id=user_id)
    job_name = None
    if job_id is not None:
        job  = job_models.Job.objects.get(id=job_id)
        job_name= job.job_title
        mail_subject = f'You Have Been Invited as Medic for {companyName}'
        job_title = ''
        if job_name is not None:
            job_title = job_name
        data  = {
            user:user,
            'domain':os.environ['domain'],
            'companyName':companyName,
            'full_name':user.full_name,
            'job_title':job_title
        }
        message = render_to_string('panelist_invite.html',context=data)

        send_mail(
            subject=mail_subject,
            html_content=message,
            sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
            to=[{"email":to_email,"name":"rel8"}])



# @shared_task()
# def handle_invite_job_seeker(user_id,to_email,companyName):
#     user = get_user_model().objects.get(id=user_id)

#     handle_invite_job_seeker(user,to_email,companyName)

@shared_task()
def handle_invite_job_seeker(user_id,to_email,companyName):
    user = get_user_model().objects.get(id=user_id)
    invite_job_seeker(user,to_email,companyName)


@shared_task()
def handle_send_application_letters(user_id,jobApplicant_id,job_title):
    user = get_user_model().objects.get(id=user_id)
    job_applicant = job_models.JobApplicant.objects.get(id=jobApplicant_id)
    job_applicant.has_sent_selection_mail=True
    job_applicant.save()
    send_application_letters(user,job_applicant.final_selection_state,job_title,job=job_applicant.job)



@shared_task()
def send_forgot_password_mail(email,link):
    mail_subject ='Forgot Password'
    user = get_user_model().objects.get(email=email)

    data ={
        'link':link,
        'full_name':user.full_name
    }
    message = render_to_string('forgot_password.html',context=data)
    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":email,"name":"rel8"}])

