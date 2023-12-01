from django.db.models.signals import post_save
from django.dispatch import receiver

from mailing.EmailConfirmation import activateEmail
from . import models
from mailing.tasks import send_activation_mail
from mailing.EmailConfirmation import activateEmail
from utils.notification import NovuProvider

@receiver(post_save, sender=models.User)
def send_confirmation_mail_to_user_after_save(sender, **kwargs):

    if kwargs['created']:
        print('Sending Boss')
        user = kwargs['instance']
        try:
            novu = NovuProvider()
            novu.subscribe(
            userID=user.id,
            email=user.email
            )
        except:pass  
        if user.user_type != 'panelist' or user.user_type != 'admin':
            # activateEmail(user,to_email=user.email)
            send_activation_mail.delay(user.id, user.email)
