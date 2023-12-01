from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_bytes,force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def send_mail(subject,html_content,sender,to):
    configuration = sib_api_v3_sdk.Configuration()
    
    # configuration.api_key['api-key']=os.environ['SENDINBLUE_API_KEY']
    configuration.api_key['api-key']=os.environ['SENDINBLUE_API_KEY']
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,html_content=html_content,
        sender=sender, subject=subject)
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

def activateEmail(user,to_email):
    mail_subject = 'Activate your user account'
    data = {
        user:user,
        'domain':os.environ['domain'],
        'uid':urlsafe_base64_encode(force_bytes(user.id)),
        'token':account_activation_token.make_token(user=user)
        # 'protocol':'https'
    }
    message = render_to_string('mail_body.html',context=data)
    
    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":to_email,"name":"rel8"}])


def activatePanelistEmail(user,to_email,password):
    mail_subject = 'You have been invited as a panelist on Squential Job'
    data = {
        user:user,
        'domain':os.environ['domain'],
        'uid':urlsafe_base64_encode(force_bytes(user.id)),
        'token':account_activation_token.make_token(user=user),
        'password':password
        # 'protocol':'https'
    }
    message = render_to_string('panelist_activate.html',context=data)
    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":to_email,"name":"rel8"}])

def invite_job_seeker(user,to_email,companyName):
    mail_subject = f'{companyName} Has Invited For an Interview on Sequntial Job APP'
    data = {
             user:user,
        'domain':os.environ['domain'],
        'companyName':companyName

    }
    message = render_to_string('job_seeker_invite.html',context=data)

    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":to_email,"name":"rel8"}])
def invitePanelist(user,to_email,companyName,job_name=None):
    mail_subject = f'You Have Been Invited as panelist for {companyName}'
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

def forgot_passwordEmail(user,to_email):
    mail_subject = 'ifflliate.store Forgot Password'

    data = {
        user:user,
        'domain':os.environ['domain'],
        'uid':urlsafe_base64_encode(force_bytes(user.id)),
        'token':account_activation_token.make_token(user=user)
        # 'protocol':'https'
    }
    message = render_to_string('forgot_password.html',context=data)

    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":to_email,"name":"rel8"}])


def handle_sending_jobseekers_new_job_reminder(user,job_title):
    mail_subject = f'New Job alert "{job_title}"'
    data = {
                user:user,
        'domain':os.environ['domain'],
        'mail_subject':mail_subject,
        'job_title':job_title
    }


    message = render_to_string('job_reminder.html',context=data)

    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":user.email,"name":"rel8"}])
def send_application_letters(user,letter_state,job_title,job=None):
    mail_subject = ''
    if letter_state=='selected':
        mail_subject=f'Congratulation Offered the job with for  {job_title}'

    if letter_state=='in_view':
        mail_subject=f'You were not Select but we would reach out to you in Future'

    if letter_state=='not_selected':
        mail_subject=f'You were not Select for the role in {job_title} '

    data = {
                user:user,
        'domain':os.environ['domain'],
        'mail_subject':mail_subject,
        'letter_state':letter_state,
        'job_title':job_title,
        'full_name':user.full_name,
        'company_name':job.company.organisation_name,
        'official_phone':job.company.official_phone
    }
    message = render_to_string('application_letter.html',context=data)
    


    send_mail(
        subject=mail_subject,
        html_content=message,
        sender=  {"email":os.environ['domain_mail'],"name":"Squential Job"},
        to=[{"email":user.email,"name":"rel8"}])