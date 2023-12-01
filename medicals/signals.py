from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from myauthentication.models import User,MedicalRepProfile
import json,random
from mailing.tasks import handle_inviteMedicalRep,handle_activateMedicEmail
import string
import random,time



@receiver(post_save,sender=models.JobMedicals)
def handle_medical_rep_creation(sender,**kwargs):
    jobmedicals =kwargs['instance']
    if kwargs['created']:
        "True if a new medic record was created."
        with transaction.atomic():
            email = jobmedicals.medical_rep
            if User.objects.filter(email=email).exists():
                'if this panelist exist already just get him and append the company that is requesting for him'
                user  = User.objects.filter(email=email).first()
                medic_rep = MedicalRepProfile.objects.get(user=user)
                medic_rep.company.add(jobmedicals.company)
                medic_rep.job.add(jobmedicals.job)
                medic_rep.save()
                handle_inviteMedicalRep.delay(
                    user_id=user.id,to_email=email,
                    companyName=jobmedicals.company.organisation_name,
                    job_id=jobmedicals.job.id
                )
            else:
                password=''.join(random.choices(string.ascii_uppercase +string.digits, k=7))
                medic = User.objects.create_medic(
                       email=email,
                        job=jobmedicals.job,
                        password=str(password),#we would randomly generate but for testing we using a static number 
                        company=jobmedicals.company
                )
                medic.save()
                handle_activateMedicEmail.delay(user_id=medic.user.id,to_email=email,password=password)

                handle_inviteMedicalRep.delay(
                user_id=medic.user.id,to_email=email,
                companyName=jobmedicals.company.organisation_name,
                job_id=jobmedicals.job.id
                )