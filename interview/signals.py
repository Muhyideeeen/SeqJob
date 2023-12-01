from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from myauthentication.models import User,PanelistProfile
import json,random
from mailing.tasks import handle_activatePanelistEmail,handle_invitePanelist
import string
import random,time

@receiver(post_save,sender=models.Interview)
def handle_panelist(sender,**kwargs):
    'this will handle panelist creation and invitation'
    interview  = kwargs['instance']
    if kwargs['created']:
        "True if a new Interview record was created."
        with transaction.atomic():
            for data in interview.list_of_email:
                email =data.get('email')
                if User.objects.filter(email=data.get('email')).exists():
                    'if this panelist exist already just get him and append the company that is requesting for him'
                    user = User.objects.filter(email=email).first()
                    panelistprofile = PanelistProfile.objects.get(user=user)
                    panelistprofile.company.add(interview.company)
                    panelistprofile.job.add(interview.job)
                    panelistprofile.save()
                    handle_invitePanelist.delay(user_id=user.id,to_email=data.get('email'),
                                                companyName=interview.company.organisation_name,job_id=interview.job.id,
                                                letter=interview.panelist_invitation_letter
                                                )
                else:
                    password =  ''.join(random.choices(string.ascii_uppercase +string.digits, k=7))
                    panelist = User.objects.create_panelist(
                        email=data.get('email'),
                        job=interview.job,
                        password=str(password),#we would randomly generate but for testing we using a static number 
                        company=interview.company
                    )
                    # panelist.job.add(interview.job)
                    panelist.save()

                    
                    handle_activatePanelistEmail.delay(user_id=panelist.user.id,to_email=data.get('email'),password=password)
                    # time.sleep(1)
                    handle_invitePanelist.delay(user_id=panelist.user.id,to_email=data.get('email'),
                                                companyName=interview.company.organisation_name,job_id=interview.job.id,
                                                letter=interview.panelist_invitation_letter
                                                )

                    "the next line should contain a async call to send maill will come to that later"

                