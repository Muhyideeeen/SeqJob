from celery import shared_task
from jobs.models import Job
from myauthentication.models import JobSeekerProfile
from mailing.EmailConfirmation import handle_sending_jobseekers_new_job_reminder
from utils.notification import NovuProvider


@shared_task()
def send_new_jobs_reminder_to_intrested_seekers(job_id:int):
    job = Job.objects.get(id=job_id)
    seekers = JobSeekerProfile.objects.filter(notify_me_on__gt='')
    for eachSeeker in seekers:
        # https://stackoverflow.com/questions/62115746/can-i-check-if-a-list-contains-any-item-from-another-list -the code below came from here
        if any(x in  eachSeeker.notify_me_on.split(',') for x in job.job_categories.split(',')):
            print(f'Send Mail About {job.job_title}')
            handle_sending_jobseekers_new_job_reminder(eachSeeker.user,job.job_title)


    # user_ids=list(map(lambda seeker:seeker.user.id, JobSeekerProfile.objects.all()))
    # novu = NovuProvider()
    # novu.send_notification(
    # name='sequential-jobs-api',
    # sub_id=user_ids,
    # title=f'Apply for {job.job_title}',
    # content='a new job has been create please apply')