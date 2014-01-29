from huey.djhuey import crontab, periodic_task
from models import Task
from datetime import timedelta
from django.utils import timezone
from fcs.backend.mailing_helper import MailingHelper
import os


@periodic_task(crontab(minute='*'))
def notify_about_crawler_data():
    t0 = timezone.now() - timedelta(hours=23)
    tasks = list(Task.objects.filter(active=True, last_data_download__lte=t0))
    tasks = tasks + list(Task.objects.filter(active=True, last_data_download=None, created__lte=t0))
    tasks.sort(key=lambda x: x.user.id)
    grouped_list = []
    usr = None
    lst = []
    for task in tasks:
        if task.user != usr:
            usr = task.user
            grouped_list.append(lst)
            lst = [task]
        else:
            lst.append(task)
    grouped_list.append(lst)
    grouped_list = grouped_list[1:]
    mh = MailingHelper('./fcs/backend/mail_templates')
    for lst in grouped_list:
        print str(lst[0].user)+" : "+", ".join([x.name for x in lst])
        mh.send_html_email('Yor crawler data is waiting', 'crawler_data',
                           {'user': str(lst[0].user), 'tasks': ", ".join([x.name for x in lst])}, 'mailbot@fcs.com',
                           [lst[0].user.email])
    print 'ok'
