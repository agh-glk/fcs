from huey.djhuey import crontab, periodic_task
from models import Task, MailSent
from datetime import timedelta
from django.utils import timezone
from fcs.backend.mailing_helper import MailingHelper
from django.conf import settings


@periodic_task(crontab(minute='*/15'))
def notify_about_crawler_data():
    earlier_23_hours = timezone.now() - timedelta(hours=23)
    tasks = list(Task.objects.filter(active=True, last_data_download__lte=earlier_23_hours))
    tasks = tasks + list(Task.objects.filter(active=True, last_data_download=None, created__lte=earlier_23_hours))
    earlier_24_hours = timezone.now() - timedelta(hours=24)
    tasks_with_users_already_notified = [list(x.tasks.all()) for x in MailSent.objects.filter(date__gte=earlier_24_hours)]
    tasks_with_users_already_notified = [x for inner_list in tasks_with_users_already_notified for x in inner_list]
    tasks_with_users_already_notified = set(tasks_with_users_already_notified).intersection(tasks)
    for task in tasks_with_users_already_notified:
        tasks.remove(task)
    if len(tasks) > 0:
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
            #print str(lst[0].user)+" : "+", ".join([x.name for x in lst])
            mh.send_html_email('Yor crawler data is waiting', 'crawler_data',
                               {'user': str(lst[0].user), 'tasks': ", ".join([x.name for x in lst])},
                               settings.MAIL_BOT_EMAIL, [lst[0].user.email])
        mail_info = MailSent.objects.create(date=timezone.now())
        mail_info.save()
        for task in tasks:
            mail_info.tasks.add(task)


@periodic_task(crontab(day='*/3'))
def remove_old_mail_data():
    two_days_earlier = timezone.now() - timedelta(days=2)
    MailSent.objects.filter(date__lte=two_days_earlier).delete()
